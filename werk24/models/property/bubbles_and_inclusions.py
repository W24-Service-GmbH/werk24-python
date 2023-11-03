from decimal import Decimal
from typing import Literal, Union

from pydantic import Field

from werk24.models.property.base import W24Property
from werk24.models.value import W24PhysicalQuantity, ureg


class W24PropertyBubblesAndInclusions(W24Property):
    """Parent for all Glas Homogeneity Properties"""

    property_type: Literal["BUBBLES_AND_INCLUSIONS"] = "BUBBLES_AND_INCLUSIONS"


class W24PropertyBubblesAndInclusionSchottGrade(W24PropertyBubblesAndInclusions):
    property_subtype: Literal["SCHOTT_GRADE"] = "SCHOTT_GRADE"
    blurb: str = Field(examples=["Standard", "VB", "EVB"])
    grade: str = Field(examples=["Standard", "VB", "EVB"])


class W24PropertyBubblesAndInclusionIso10110Grade(W24PropertyBubblesAndInclusions):
    property_subtype: Literal["ISO_10110_GRADE"] = "ISO_10110_GRADE"
    blurb: str = Field(examples=["1/3 x 0.5"])
    number_of_largest_permissible_bubbles: int = Field(examples=[3])
    largest_permissible_bubble_grade: Decimal = Field(examples=[Decimal("0.5")])


class W24PropertyBubblesAndInclusionsIso10110Limits(W24PropertyBubblesAndInclusions):
    property_subtype: Literal["ISO_10110_LIMITS"] = "ISO_10110_LIMITS"
    blurb: str = Field(examples=["30/100 cm3 & 0.1mm2/100cm3"])
    number_of_largest_permissible_bubbles: int = Field(examples=[30])
    total_cross_section: W24PhysicalQuantity = Field(
        examples=[W24PhysicalQuantity(blurb="0.1mm2", value=0.1 * ureg.mm**2)]
    )
    test_volume: W24PhysicalQuantity = Field(
        examples=[W24PhysicalQuantity(blurb="100cm3", value=100 * ureg.cm**3)]
    )


W24PropertyBubblesAndInclusionsType = Union[
    W24PropertyBubblesAndInclusionSchottGrade,
    W24PropertyBubblesAndInclusionIso10110Grade,
    W24PropertyBubblesAndInclusionsIso10110Limits,
]
