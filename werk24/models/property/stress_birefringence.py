from typing import Literal, Union

from pydantic import Field

from werk24.models.property.base import W24Property
from werk24.models.value import W24PhysicalQuantity, ureg


class W24PropertyStressBirefringence(W24Property):
    """Parent for all Glass Homogeneity Properties"""

    property_type: Literal["STRESS_BIREFRINGENCE"] = "STRESS_BIREFRINGENCE"


class W24PropertyStressBirefringenceIso10110Value(W24PropertyStressBirefringence):
    """ISO 10110 Stress Birefringence Value"""

    property_subtype: Literal["ISO_10110_VALUE"] = "ISO_10110_VALUE"
    blurb: str = Field(examples=["0/8"])
    value: W24PhysicalQuantity = Field(
        examples=[W24PhysicalQuantity(blurb="8nm/cm", value=8 * ureg.nm / ureg.cm)]
    )


class W24PropertyStressBirefringenceIso10110Grade(W24PropertyStressBirefringence):
    """ISO 10110 Stress Birefringence Grade"""

    property_subtype: Literal["ISO_10110_GRADE"] = "ISO_10110_GRADE"
    blurb: str = Field(examples=["SB20", "SB02"])
    grade: str = Field(examples=["SB20", "SB02"])


W24PropertyStressBirefringenceType = Union[
    W24PropertyStressBirefringenceIso10110Value,
    W24PropertyStressBirefringenceIso10110Grade,
]
