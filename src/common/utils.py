"""
Utility functions for the law-ai project.
"""

import json
from pathlib import Path
from typing import Generator, List
from uuid import UUID

from httpx import URL

from src.common import config
from src.common.types import (
    DocumentAugmented,
    DocumentLabeled,
    DocumentParsed,
    DocumentText,
    ScrapingID,
)


def flatten_text(text: str) -> str:
    """
    Remove extra spaces from the text.
    """
    return " ".join(text.split())


def get_document_path(document_id: UUID) -> Path:
    """
    Get the path to the document PDF file based on its ID.
    """
    return (config.DOCS_DIR / str(document_id)).with_suffix(".pdf")


def _read_jsonl(fp: Path) -> Generator[dict, None, None]:
    """
    Read a JSONL file and yield each entry as a dictionary.
    """
    with fp.open("r", encoding="utf-8") as f:
        for line in f:
            entry = json.loads(line)
            if entry_id := entry.get("id"):
                entry["id"] = UUID(entry_id)
            if entry_url := entry.get("url"):
                entry["url"] = URL(entry_url)

            yield entry


def load_scraping_ids() -> List[ScrapingID]:
    """
    Load the scraping IDs.
    """
    return [
        ScrapingID(**scraping_id) for scraping_id in _read_jsonl(config.CASE_IDS_JSONL)
    ]


def load_documents_text() -> List[DocumentText]:
    """
    Load the documents text.
    """
    return [
        DocumentText(**doc_text) for doc_text in _read_jsonl(config.DOCS_TEXT_JSONL)
    ]


def load_documents_parsed() -> List[DocumentParsed]:
    """
    Load the parsed documents.
    """
    return [
        DocumentParsed(**doc_parsed)
        for doc_parsed in _read_jsonl(config.DOCS_PARSED_JSONL)
    ]


def load_documents_labeled() -> List[DocumentLabeled]:
    """
    Load the labeled documents.
    """
    return [
        DocumentLabeled(**doc_labeled)
        for doc_labeled in _read_jsonl(config.DOCS_LABELED_JSONL)
    ]


def load_documents_augmented() -> List[DocumentAugmented]:
    """
    Load the augmented documents.
    """
    return [
        DocumentAugmented(**doc_augmented)
        for doc_augmented in _read_jsonl(config.DOCS_AUGMENTED_JSONL)
    ]
