"""
This module contains the type definitions used in the package.
"""

from enum import Enum
from typing import TypedDict, Literal
from uuid import UUID

from httpx import URL


class Message(TypedDict):
    role: Literal["system", "user", "assistant"]
    content: str


class LegalPartyType(str, Enum):
    INDIVIDUAL = "individual"
    MULTIPLE_INDIVIDUALS = "multiple_individuals"
    LEGAL_ENTITY = "legal_entity"
    PUBLIC_ENTITY = "public_entity"
    OTHER = "other"


class GrammaticalGender(str, Enum):
    MASCULINE = "masculine"
    FEMININE = "feminine"
    NEUTER = "neuter"


class Appellant(str, Enum):
    PLAINTIFF = "plaintiff"
    DEFENDANT = "defendant"
    BOTH = "both"
    OTHER = "other"


class Decision(str, Enum):
    UPHELD = "upheld"
    REVERSED = "reversed"
    OTHER = "other"


class ScrapingID(TypedDict):
    id: UUID
    year: int
    case_number: str
    url: URL


class DocumentText(ScrapingID):
    text: str


class DocumentParsed(DocumentText):
    facts: str
    operative: str


class DocumentLabeled(DocumentParsed):
    plaintiff_type: LegalPartyType
    plaintiff_gender: GrammaticalGender
    defendant_type: LegalPartyType
    defendant_gender: GrammaticalGender
    appellant: Appellant
    appellant_type: LegalPartyType | None
    appellant_gender: GrammaticalGender | None
    decision: Decision


class DocumentAugmented(DocumentLabeled):
    facts_augmented: str
