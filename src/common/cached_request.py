"""
This module provides a function to perform HTTP GET requests with caching
and retry logic using the httpx library. The caching mechanism stores
the response content in a gzip-compressed file, which is saved in a
specified cache directory. The function uses a semaphore to limit
concurrent requests when specified. The retry logic is implemented using
the tenacity library, which allows for exponential backoff and
customizable retry conditions.
"""

import asyncio
import gzip
import hashlib
from typing import Optional

from httpx import AsyncClient, HTTPError, URL
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_random_exponential,
)

from src.common import config

config.SCRAPING_CACHE.mkdir(parents=True, exist_ok=True)


@retry(
    stop=stop_after_attempt(5),
    wait=wait_random_exponential(multiplier=60),
    reraise=True,
    retry=retry_if_exception_type(HTTPError),
)
async def get(
    url: URL,
    client: AsyncClient,
    sem: Optional[asyncio.Semaphore] = None,
) -> bytes:
    """
    Fetch content from the given URL using a httpx.AsyncClient with optional caching.
    """
    cache_key = hashlib.md5(f"GET:{url}".encode()).hexdigest()
    if (content := _get_cache(cache_key)) is not None:
        return content

    # If a semaphore is provided, we acquire it to limit concurrency
    if sem:
        async with sem:
            response = await client.get(url)
    else:
        response = await client.get(url)

    response.raise_for_status()
    content = response.content
    _set_cache(cache_key, content)

    return content


def _get_cache(key: str) -> Optional[bytes]:
    """
    Retrieve cached content from the cache directory.
    """
    try:
        with gzip.open(config.SCRAPING_CACHE / f"{key}.gz", "rb") as f:
            return f.read()
    except FileNotFoundError:
        return None


def _set_cache(key: str, value: bytes):
    with gzip.open(config.SCRAPING_CACHE / f"{key}.gz", "wb") as f:
        f.write(value)
