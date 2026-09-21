from typing import Literal, Union

from pydantic import Field

from ..property.base import W24Property
from ..value import W24PhysicalQuantity


class W24PropertyStressBirefringence(W24Property):
    """Parent for all Glass Homogeneity Properties"""

    property_type: Literal["STRESS_BIREFRINGENCE"] = "STRESS_BIREFRINGENCE"


class W24PropertyStressBirefringenceIso10110Value(W24PropertyStressBirefringence):
    """ISO 10110 Stress Birefringence Value"""

    property_subtype: Literal["ISO_10110_VALUE"] = "ISO_10110_VALUE"
    blurb: str = Field(examples=["0/8"])
    # Serialized form; see the note in ``bubbles_and_inclusions``.
    value: W24PhysicalQuantity = Field(
        examples=[
            {
                "blurb": "8nm/cm",
                "value": "8.0 nanometer / centimeter",
                "tolerance": None,
            }
        ]
    )


class W24PropertyStressBirefringenceIso10110Grade(W24PropertyStressBirefringence):
    """ISO 10110 Stress Birefringence Grade"""

    property_subtype: Literal["ISO_10110_GRADE"] = "ISO_10110_GRADE"
    blurb: str = Field(examples=["SB20", "SB02"])
    grade: str = Field(examples=["SB20", "SB02"])


class W24PropertyStressBirefringenceFreeText(W24PropertyStressBirefringence):
    """Stress Birefringence Free Text"""

    free_text: str
    variation_type: Literal["FREETEXT"] = "FREETEXT"


W24PropertyStressBirefringenceType = Union[
    W24PropertyStressBirefringenceIso10110Value,
    W24PropertyStressBirefringenceIso10110Grade,
    W24PropertyStressBirefringenceFreeText,
]
