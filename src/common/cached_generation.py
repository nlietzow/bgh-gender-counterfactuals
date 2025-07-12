"""
This module provides functions to interact with OpenAI's API for generating
"""

import asyncio
import json
import pickle
from enum import Enum
from hashlib import md5
from typing import Optional, TypeVar

from openai import AsyncOpenAI, APIConnectionError, RateLimitError
from pydantic import BaseModel
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_random_exponential,
)

from src.common import config
from src.common.types import Message

client = AsyncOpenAI(api_key=config.OPENAI_API_KEY)
T = TypeVar("T", bound=BaseModel)

config.GENERATION_CACHE.mkdir(parents=True, exist_ok=True)


class Model(str, Enum):
    GPT_41 = "gpt-4.1-2025-04-14"
    GPT_41_MINI = "gpt-4.1-mini-2025-04-14"


async def create(
    model: Model,
    messages: list[Message],
    prediction_content: str = "",
    temperature: float = 0.0,
    sem: Optional[asyncio.Semaphore] = None,
) -> str:
    """
    Create a response using the specified model and messages.
    """
    messages_dumps = tuple(json.dumps(m, sort_keys=True) for m in messages)
    cache_key = md5(
        f"CREATE:{model.value}:{temperature}:{messages_dumps}:{prediction_content}".encode(
            "utf-8"
        )
    ).hexdigest()

    if (completion := _get_cache(cache_key)) is None:
        response = await _run_with_sema(
            sem,
            client.chat.completions.create,
            model=model.value,
            temperature=temperature,
            messages=messages,
            logprobs=True if not prediction_content else False,
            top_logprobs=3 if not prediction_content else None,
            timeout=60,
            prediction=(
                {"type": "content", "content": prediction_content}
                if prediction_content
                else None
            ),
        )
        completion = response.model_dump(mode="json")
        _set_cache(cache_key, completion)

    return completion["choices"][0]["message"]["content"]


async def parse(
    model: Model,
    messages: list[Message],
    response_format: type[T],
    temperature: float = 0.0,
    sem: Optional[asyncio.Semaphore] = None,
) -> T:
    """
    Parse the messages using the specified model and response format.
    """
    messages_dumps = tuple(json.dumps(m, sort_keys=True) for m in messages)
    schema = json.dumps(response_format.model_json_schema(), sort_keys=True)
    cache_key = md5(
        f"PARSE:{model.value}:{temperature}:{messages_dumps}:{schema}".encode(
            encoding="utf-8"
        )
    ).hexdigest()

    if (completion := _get_cache(cache_key)) is None:
        response = await _run_with_sema(
            sem,
            client.beta.chat.completions.parse,
            model=model.value,
            temperature=temperature,
            messages=messages,
            response_format=response_format,
            logprobs=True,
            top_logprobs=3,
            timeout=60,
        )
        completion = response.model_dump(mode="json")
        _set_cache(cache_key, completion)

    return response_format(**completion["choices"][0]["message"]["parsed"])


@retry(
    stop=stop_after_attempt(10),
    wait=wait_random_exponential(multiplier=60),
    reraise=True,
    retry=retry_if_exception_type((APIConnectionError, RateLimitError)),
)
async def _run_with_sema(sem: asyncio.Semaphore, fct: callable, **kwargs):
    """
    Run a function with a semaphore to limit the number of concurrent requests.
    """
    async with sem:
        return await fct(**kwargs)


def _get_cache(key: str) -> Optional[dict]:
    """
    Get the cached completion from the cache file.
    """
    try:
        with open(config.GENERATION_CACHE / f"{key}.pkl", "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None


def _set_cache(key: str, completion: dict):
    """
    Set the cached completion in the cache file.
    """
    with open(config.GENERATION_CACHE / f"{key}.pkl", "wb") as f:
        f.write(pickle.dumps(completion))
