"""
Label documents with case information using the GPT-4o model.
"""

import asyncio
import json
from itertools import batched

from tqdm.auto import tqdm

from src.common import cached_generation, config, prompts
from src.common.types import Appellant, DocumentLabeled, DocumentParsed, Message
from src.common.utils import load_documents_parsed
from src.labeling._model import CaseInfo


async def label_docs():
    """
    Main function to label documents with case information.
    """
    sem = asyncio.Semaphore(10)
    docs_parsed = load_documents_parsed()

    # noinspection DuplicatedCode
    async def generate():
        with tqdm(total=len(docs_parsed)) as pbar:
            for batch in batched(docs_parsed, 25):
                tasks = (_process(doc, sem) for doc in batch)
                for r in await asyncio.gather(*tasks):
                    pbar.update(1)
                    yield r

    results = [r async for r in generate()]
    content = "\n".join(json.dumps(r, default=lambda x: str(x)) for r in results)
    config.DOCS_LABELED_JSONL.write_text(content, encoding="utf-8")

    return results


async def _process(doc: DocumentParsed, sem: asyncio.Semaphore):
    """
    Process a single document to extract case information.
    """
    messages = [
        Message(
            role="system",
            content=prompts.CREATE_CASE_INFO_SYSTEM,
        ),
        Message(
            role="user",
            content=prompts.CREATE_CASE_INFO_USER.format(
                FACTS=doc["facts"],
                DECISION=doc["operative"],
            ),
        ),
    ]
    r = await cached_generation.parse(
        model=cached_generation.Model.GPT_41,
        messages=messages,
        response_format=CaseInfo,
        sem=sem,
    )
    if r.appellant == Appellant.PLAINTIFF:
        appellant_type = r.plaintiff.type
        appellant_gender = r.plaintiff.grammatical_gender
    elif r.appellant == Appellant.DEFENDANT:
        appellant_type = r.defendant.type
        appellant_gender = r.defendant.grammatical_gender
    else:
        appellant_type = None
        appellant_gender = None

    return DocumentLabeled(
        **doc,
        plaintiff_type=r.plaintiff.type,
        plaintiff_gender=r.plaintiff.grammatical_gender,
        defendant_type=r.defendant.type,
        defendant_gender=r.defendant.grammatical_gender,
        appellant=r.appellant,
        appellant_type=appellant_type,
        appellant_gender=appellant_gender,
        decision=r.decision,
    )
