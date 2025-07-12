"""
This module defines the data models and associated descriptions used
for annotating legal case information for downstream processing.
"""

from pydantic import BaseModel, Field

from src.common.types import Appellant, Decision, GrammaticalGender, LegalPartyType

TYPE_DESC = f"""
Specifies the type of party involved in the case. One of:

- "{LegalPartyType.INDIVIDUAL.value}": A single natural person.
- "{LegalPartyType.MULTIPLE_INDIVIDUALS.value}": Two or more natural persons acting together.
- "{LegalPartyType.LEGAL_ENTITY.value}": A company, organization, or other legally recognized entity (e.g., corporations, associations).
- "{LegalPartyType.PUBLIC_ENTITY.value}": A government agency, municipality, or other public-sector institution.
- "{LegalPartyType.OTHER.value}": Any other type of party not covered by the categories above.
""".strip()

GRAMMAR_DESC = f"""
Specifies the grammatical gender used to refer to this party in legal texts. One of:

- "{GrammaticalGender.MASCULINE.value}": Used when the party is referred to with masculine grammatical forms.
  Example: "Der Kläger" (the male plaintiff), "Der Beklagte" (the male defendant).
- "{GrammaticalGender.FEMININE.value}": Used when the party is referred to with feminine grammatical forms.
  Example: "Die Klägerin" (the female plaintiff), "Die Beklagte" (the female defendant).
- "{GrammaticalGender.NEUTER.value}": Used when the party is referred to with neuter grammatical forms.
  Example: "Das Unternehmen" (the company), "Das Gericht" (the court).

Note: The grammatical gender does not necessarily reflect biological gender but follows conventional usage in legal German.
""".strip()

APPELLANT_DESC = f"""
Indicates which party filed the appeal. One of:

- "{Appellant.PLAINTIFF.value}": The appeal was filed by the plaintiff.
- "{Appellant.DEFENDANT.value}": The appeal was filed by the defendant.
- "{Appellant.BOTH.value}": Both plaintiff and defendant filed appeals.
- "{Appellant.OTHER.value}": Any other scenario (e.g., third parties, state interventions).
""".strip()

DECISION_DESC = f"""
Specifies the result of the appeal. One of:

- "{Decision.REVERSED.value}": The appellate court overturned the lower court’s decision and typically remanded the case for further proceedings.
- "{Decision.UPHELD.value}": The appellate court confirmed the lower court’s decision; no changes were made.
- "{Decision.OTHER.value}": Any other result, including mixed outcomes (e.g., partially upheld and partially reversed), or where the decision cannot be clearly categorized.
""".strip()


class PartyInfo(BaseModel):
    type: LegalPartyType = Field(description=TYPE_DESC)
    grammatical_gender: GrammaticalGender = Field(description=GRAMMAR_DESC)


class CaseInfo(BaseModel):
    plaintiff: PartyInfo = Field(
        description="Information about the plaintiff extracted from the case text."
    )
    defendant: PartyInfo = Field(
        description="Information about the defendant extracted from the case text."
    )
    appellant: Appellant = Field(description=APPELLANT_DESC)
    decision: Decision = Field(description=DECISION_DESC)
