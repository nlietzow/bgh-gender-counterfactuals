"""
This script generates augmentations for training examples by modifying the tatbestand based on the
grammatical gender of the appellant. It uses a language model to create these augmentations and saves the
results in JSONL format. The augmentations are then zipped for easier distribution.
"""

import asyncio
import json
from itertools import batched

from tqdm import tqdm

from src.augmentation._prompt import AugmentationPrompt
from src.common import prompts
from src.common import config, cached_generation
from src.common.types import (
    Appellant,
    GrammaticalGender,
    LegalPartyType,
    DocumentAugmented,
    DocumentLabeled,
    Decision,
)
from src.common.utils import flatten_text, load_documents_labeled

prompt = AugmentationPrompt(prompts.CREATE_AUGMENTATION_SYSTEM)


async def create_augmentations():
    """
    Main function to generate augmentations for training examples.
    """
    sem = asyncio.Semaphore(10)

    async def generate(examples: list[DocumentLabeled]):
        with tqdm(total=len(examples)) as pbar:
            for batch in batched(examples, 25):
                tasks = (_process(doc, sem) for doc in batch)
                for r in await asyncio.gather(*tasks):
                    pbar.update(1)
                    if r is not None:
                        yield r

    # Load examples
    documents_labeled = load_documents_labeled()
    augmentations = [r async for r in generate(documents_labeled)]

    # Write augmentations to files
    config.DOCS_AUGMENTED_JSONL.write_text(
        "\n".join(json.dumps(r, default=lambda x: str(x)) for r in augmentations),
        encoding="utf-8",
    )

    return augmentations


async def _process(doc: DocumentLabeled, sem) -> DocumentAugmented | None:
    """
    Process a single training example to create an augmentation.
    """
    if (
        doc["appellant"] not in (Appellant.PLAINTIFF, Appellant.DEFENDANT)
        or doc["decision"] == Decision.OTHER
        or doc["appellant_type"] != LegalPartyType.INDIVIDUAL
        or doc["appellant_gender"] == GrammaticalGender.NEUTER
    ):
        return None

    system_prompt = prompt.system_prompt(
        appellant=Appellant(doc["appellant"]),
        grammatical_gender=GrammaticalGender(doc["appellant_gender"]),
    )
    response = await cached_generation.create(
        model=cached_generation.Model.GPT_41_MINI,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": doc["facts"]},
        ],
        prediction_content=doc["facts"],
        sem=sem,
    )
    return DocumentAugmented(
        **doc,
        facts_augmented=flatten_text(response),
    )
