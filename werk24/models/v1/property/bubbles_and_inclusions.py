from decimal import Decimal
from typing import Literal, Optional, Union

from pydantic import Field

from ..value import W24PhysicalQuantity
from .base import W24Property


class W24PropertyBubblesAndInclusions(W24Property):
    """Parent for all Bubbles and Inclusions Properties"""

    property_type: Literal["BUBBLES_AND_INCLUSIONS"] = "BUBBLES_AND_INCLUSIONS"


class W24PropertyBubblesAndInclusionsSchottGrade(W24PropertyBubblesAndInclusions):
    """Bubbles and Inclusions Schott Grade"""

    property_subtype: Literal["SCHOTT_GRADE"] = "SCHOTT_GRADE"
    blurb: str = Field(examples=["Standard", "VB", "EVB"])
    grade: str = Field(examples=["Standard", "VB", "EVB"])


class W24PropertyBubblesAndInclusionsIso10110Grade(W24PropertyBubblesAndInclusions):
    """Bubbles and Inclusions ISO 10110 Grade"""

    property_subtype: Literal["ISO_10110_GRADE"] = "ISO_10110_GRADE"
    blurb: str = Field(examples=["1/3 x 0.5"])
    number_of_largest_permissible_bubbles: int = Field(examples=[3])
    largest_permissible_bubble_grade: Decimal = Field(examples=[Decimal("0.5")])


class W24PropertyBubblesAndInclusionsIso10110Limits(W24PropertyBubblesAndInclusions):
    """Bubbles and Inclusions ISO 10110 Limits"""

    property_subtype: Literal["ISO_10110_LIMITS"] = "ISO_10110_LIMITS"
    blurb: str = Field(examples=["30/100 cm3 & 0.1mm2/100cm3"])
    number_of_largest_permissible_bubbles: Optional[int] = Field(
        examples=[30], default=None
    )
    # Serialized form rather than a constructed W24PhysicalQuantity: building
    # one here would touch the pint registry at import. See
    # ``werk24.models.v1.value`` for the 182ms that costs, and
    # ``tests/test_lazy_unit_registry.py`` for the schemas this keeps equal.
    total_cross_section: W24PhysicalQuantity = Field(
        examples=[
            {"blurb": "0.1mm2", "value": "0.1 millimeter ** 2", "tolerance": None}
        ]
    )
    test_volume: W24PhysicalQuantity = Field(
        examples=[
            {"blurb": "100cm3", "value": "100 centimeter ** 3", "tolerance": None}
        ]
    )


class W24PropertyBubblesAndInclusionsFreeText(W24PropertyBubblesAndInclusions):
    """Bubbles and Inclusions Free Text"""

    free_text: str
    variation_type: Literal["FREETEXT"] = "FREETEXT"


W24PropertyBubblesAndInclusionsType = Union[
    W24PropertyBubblesAndInclusionsFreeText,
    W24PropertyBubblesAndInclusionsIso10110Grade,
    W24PropertyBubblesAndInclusionsIso10110Limits,
    W24PropertyBubblesAndInclusionsSchottGrade,
]
