"""
Parse BGH Urteil documents from the BGH website.
This script extracts the tenor and tatbestand from the documents and saves them in a JSONL file.
It uses regex patterns to identify the relevant sections of the text.
The script is designed to work with documents that follow a specific format, and it will return None for documents that do not match this format.
"""

import json
import re
from typing import Generator, Optional

import spacy
from tqdm import tqdm

from src.common import config
from src.common.types import DocumentParsed, DocumentText
from src.common.utils import flatten_text, load_documents_text

NLP = spacy.load("de_core_news_lg")

URTEIL_PATTERN = re.compile(
    r"\s*(?:\S+\s+)?BUNDESGERICHTSHOF\s+IM\s+NAMEN\s+DES\s+VOLKES\s+URTEIL\s+",
    re.IGNORECASE,
)
TENOR_TATBESTAND_PATTERN = re.compile(
    r"für\s+recht\s+erkannt\s*:?"
    r"\s*\n(.+?)\n\s*"
    r"(?:von\s+rechts\s+wegen\s+.*)?"
    r"tatbestand\s*:?"
    r"\s*\n(.+?)\n\s*"
    r"entscheidungsgründe\s*:?"
    r"\s*\n.*",
    re.DOTALL | re.IGNORECASE,
)
LINE_BREAK_PATTERN = re.compile(r"(\w+)-\s+(\w+)")


def parse_docs():
    """
    Main function to parse BGH Urteil documents.
    """

    def generate() -> Generator[DocumentParsed, None, None]:
        for document_text in tqdm(load_documents_text(), desc="Parsing documents"):
            if document_parsed := _parse(document_text):
                yield document_parsed

    results = list(generate())
    content = "\n".join(json.dumps(r, default=lambda x: str(x)) for r in results)
    config.DOCS_PARSED_JSONL.write_text(content, encoding="utf-8")

    return results


def _parse(doc_text: DocumentText) -> Optional[DocumentParsed]:
    """
    Attempts to parse the PDF document for a valid BGH Urteil. Returns an Urteil object
    or None if parsing fails or the document doesn't match the known pattern.
    """
    # Quick check if it's a BGH Urteil
    if not URTEIL_PATTERN.match(doc_text["text"]):
        return None

    match = TENOR_TATBESTAND_PATTERN.search(doc_text["text"])
    if not match:
        return None

    operative, facts = match.groups()
    operative = _process(operative)
    facts = _process(facts)

    if not operative or not facts:
        raise ValueError(f"Empty tenor/tatbestand for {doc_text['id']}")

    return DocumentParsed(
        **doc_text,
        facts=facts,
        operative=operative,
    )


def _process(text: str) -> str:
    """
    Final cleanup for tenor/tatbestand: remove extraneous hyphens, strip whitespace, etc.
    """
    text = re.sub(r"(\b)\.{3,}(\b)", "\1…\2", text)
    text = re.sub(r"…[…\s]*…", r"…", text)
    text = re.sub(r"\.[.\s]*\.", r".", text)
    text = re.sub(r"\s+([.,;:!?)\]}/])", r"\1", text)
    text = re.sub(r"([(\[{/])\s+", r"\1", text)

    text = flatten_text(text)
    text = LINE_BREAK_PATTERN.sub(_fix_linebreaks, text)

    return text.strip()


def _fix_linebreaks(match):
    """
    Fixes line breaks in the text by checking the token shapes and conjunctions.
    """
    doc = NLP(match.group(0))
    assert len(doc) == 2, "Expected two tokens in the doc."
    if doc[1].pos_ == "CCONJ" or doc[1].text == "bzw":
        return match.group(0)
    elif doc[0].shape_.endswith("x-") and doc[1].shape_.startswith("x"):
        return match.group(1) + match.group(2)
    return match.group(0).replace(" ", "")
