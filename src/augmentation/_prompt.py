"""
This script defines the AugmentationPrompt class, which is used to generate
system prompts for a language model.
"""

from typing import TypedDict

from src.common.types import Appellant, GrammaticalGender


class Placeholders(TypedDict):
    appellant: str
    example_text_original: str
    example_text_revised: str
    from_appellant: str
    from_grammatical_gender: str
    not_appellant: str
    to_appellant: str
    to_grammatical_gender: str


EXAMPLE_TEXT_PLAINTIFF_M_ORIG = (
    "Der Kläger hat seinen Antrag gestellt. "
    "Er argumentiert, dass der Beklagte verantwortlich ist."
)
EXAMPLE_TEXT_PLAINTIFF_M_REV = (
    "Die Klägerin hat ihren Antrag gestellt. "
    "Sie argumentiert, dass der Beklagte verantwortlich ist."
)
EXAMPLE_TEXT_PLAINTIFF_F_ORIG = (
    "Die Klägerin hat ihren Antrag gestellt. "
    "Sie argumentiert, dass die Beklagte verantwortlich ist."
)
EXAMPLE_TEXT_PLAINTIFF_F_REV = (
    "Der Kläger hat seinen Antrag gestellt. "
    "Er argumentiert, dass die Beklagte verantwortlich ist."
)
EXAMPLE_TEXT_DEFENDANT_M_ORIG = (
    "Der Beklagte hat seinen Antrag gestellt. "
    "Er argumentiert, dass der Kläger verantwortlich ist."
)
EXAMPLE_TEXT_DEFENDANT_M_REV = (
    "Die Beklagte hat ihren Antrag gestellt. "
    "Sie argumentiert, dass der Kläger verantwortlich ist."
)
EXAMPLE_TEXT_DEFENDANT_F_ORIG = (
    "Die Beklagte hat ihren Antrag gestellt. "
    "Sie argumentiert, dass die Klägerin verantwortlich ist."
)
EXAMPLE_TEXT_DEFENDANT_F_REV = (
    "Der Beklagte hat seinen Antrag gestellt. "
    "Er argumentiert, dass die Klägerin verantwortlich ist."
)


class AugmentationPrompt:
    def __init__(self, template: str):
        self.template = template

    @property
    def plaintiff_masculine(self):
        placeholders = Placeholders(
            appellant=Appellant.PLAINTIFF.value,
            not_appellant=Appellant.DEFENDANT.value,
            from_grammatical_gender=GrammaticalGender.MASCULINE.value,
            to_grammatical_gender=GrammaticalGender.FEMININE.value,
            from_appellant="Der Kläger",
            to_appellant="Die Klägerin",
            example_text_original=EXAMPLE_TEXT_PLAINTIFF_M_ORIG,
            example_text_revised=EXAMPLE_TEXT_PLAINTIFF_M_REV,
        )
        return self.template.format(**placeholders)

    @property
    def plaintiff_feminine(self):
        placeholders = Placeholders(
            appellant=Appellant.PLAINTIFF.value,
            not_appellant=Appellant.DEFENDANT.value,
            from_grammatical_gender=GrammaticalGender.FEMININE.value,
            to_grammatical_gender=GrammaticalGender.MASCULINE.value,
            from_appellant="Die Klägerin",
            to_appellant="Der Kläger",
            example_text_original=EXAMPLE_TEXT_PLAINTIFF_F_ORIG,
            example_text_revised=EXAMPLE_TEXT_PLAINTIFF_F_REV,
        )
        return self.template.format(**placeholders)

    @property
    def defendant_masculine(self):
        placeholders = Placeholders(
            appellant=Appellant.DEFENDANT.value,
            not_appellant=Appellant.PLAINTIFF.value,
            from_grammatical_gender=GrammaticalGender.MASCULINE.value,
            to_grammatical_gender=GrammaticalGender.FEMININE.value,
            from_appellant="Der Beklagte",
            to_appellant="Die Beklagte",
            example_text_original=EXAMPLE_TEXT_DEFENDANT_M_ORIG,
            example_text_revised=EXAMPLE_TEXT_DEFENDANT_M_REV,
        )
        return self.template.format(**placeholders)

    @property
    def defendant_feminine(self):
        placeholders = Placeholders(
            appellant=Appellant.DEFENDANT.value,
            not_appellant=Appellant.PLAINTIFF.value,
            from_grammatical_gender=GrammaticalGender.FEMININE.value,
            to_grammatical_gender=GrammaticalGender.MASCULINE.value,
            from_appellant="Die Beklagte",
            to_appellant="Der Beklagte",
            example_text_original=EXAMPLE_TEXT_DEFENDANT_F_ORIG,
            example_text_revised=EXAMPLE_TEXT_DEFENDANT_F_REV,
        )
        return self.template.format(**placeholders)

    def system_prompt(
        self, appellant: Appellant, grammatical_gender: GrammaticalGender
    ):
        match appellant, grammatical_gender:
            case (Appellant.PLAINTIFF, GrammaticalGender.MASCULINE):
                return self.plaintiff_masculine
            case (Appellant.PLAINTIFF, GrammaticalGender.FEMININE):
                return self.plaintiff_feminine
            case (Appellant.DEFENDANT, GrammaticalGender.MASCULINE):
                return self.defendant_masculine
            case (Appellant.DEFENDANT, GrammaticalGender.FEMININE):
                return self.defendant_feminine
            case _:
                raise ValueError(
                    "Invalid combination of appellant and grammatical gender."
                )
