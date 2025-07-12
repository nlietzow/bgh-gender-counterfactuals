"""
Extracts text from PDF documents using PyMuPDF and saves the results in a JSONL file.
"""

import json
import re
from pathlib import Path
from typing import Generator, Optional

import pymupdf
from tqdm import tqdm

from src.common import config
from src.common.types import DocumentText
from src.common.utils import flatten_text, get_document_path, load_scraping_ids

pymupdf.TOOLS.mupdf_display_errors(False)

PAGE_NUMBER_PATTERN = re.compile(r"^-\s*\d+\s*-$", re.MULTILINE)
PARAGRAPH_NUMBER_PATTERN = re.compile(r"^\d+$", re.MULTILINE)
TOO_MANY_NEWLINES_PATTERN = re.compile(r"\n{3,}", re.MULTILINE)


def extract_text():
    """
    Main function to extract text from PDF documents.
    """

    def generate() -> Generator[DocumentText, None, None]:
        for scraping_id in tqdm(load_scraping_ids(), desc="Extracting text"):
            fp = get_document_path(scraping_id["id"])
            if text := _read(fp):
                yield DocumentText(
                    **scraping_id,
                    text=text,
                )

    results = list(generate())
    content = "\n".join(json.dumps(r, default=lambda x: str(x)) for r in results)
    config.DOCS_TEXT_JSONL.write_text(content, encoding="utf-8")

    return results


def _read(document_path: Path) -> Optional[str]:
    """
    Reads and cleans up the text from the PDF using PyMuPDF.
    """
    try:
        pages = pymupdf.get_text(path=document_path)
    except pymupdf.FileDataError as e:
        print(f"Error reading {document_path}: {e}")
        return None

    # Join pages with some spacing so that paragraphs don't merge
    text = "\n\n".join(p for p in pages if p.strip())

    # Strip each line to remove leading/trailing spaces
    text = "\n".join(map(flatten_text, text.splitlines()))

    # Apply regex replacements for typical noise
    text = PAGE_NUMBER_PATTERN.sub("", text)
    text = PARAGRAPH_NUMBER_PATTERN.sub("", text)
    text = TOO_MANY_NEWLINES_PATTERN.sub("\n\n", text)

    return text.strip()
