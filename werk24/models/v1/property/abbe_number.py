from decimal import Decimal
from typing import Any, Literal, Optional, Union

from pydantic import Field

from ..typed_model import W24TypedModel
from .base import W24Property
from .fraunhofer import W24FraunhoferLine


class W24PropertyAbbeTolerance(W24TypedModel):
    class Config:
        discriminators = ("abbe_tolerance_type",)

    blurb: str
    abbe_tolerance_type: Any


class W24PropertyAbbeToleranceValue(W24PropertyAbbeTolerance):
    """Abbe Tolerance Value"""

    abbe_tolerance_type: Literal["VALUE"] = "VALUE"
    blurb: str = Field(examples=["±0.8%"])
    deviation_upper: Optional[Decimal] = Field(examples=[Decimal("0.8")], default=None)
    deviation_lower: Optional[Decimal] = Field(examples=[Decimal("-0.8")], default=None)


class W24PropertyAbbeToleranceStep(W24PropertyAbbeTolerance):
    """Abbe Tolerance Step"""

    abbe_tolerance_type: Literal["STEP"] = "STEP"
    blurb: str = Field(examples=["Step 3", "Step 0.5"])
    step: Decimal = Field(examples=[Decimal("3"), Decimal("0.5")])


class W24PropertyAbbeToleranceFreeText(W24PropertyAbbeTolerance):
    """Abbe Tolerance Free Text"""

    free_text: str
    variation_type: Literal["FREETEXT"] = "FREETEXT"


W24PropertyAbbeToleranceType = Union[
    W24PropertyAbbeToleranceValue,
    W24PropertyAbbeToleranceStep,
    W24PropertyAbbeToleranceFreeText,
]


class W24PropertyAbbeValue(W24Property):
    property_type: Literal["ABBE_NUMBER"] = "ABBE_NUMBER"


class W24PropertyAbbeValueNumberValue(W24PropertyAbbeValue):
    """Abbe Value Number"""

    property_subtype: Literal["VALUE"] = "VALUE"

    blurb: str = Field(examples=["vd = 34.70 ±0.8%", "ve = 57.27 ±0.5%"])

    line: Optional[W24FraunhoferLine] = Field(
        examples=[
            W24FraunhoferLine.D_LINE,
            W24FraunhoferLine.E_LINE,
        ],
        default=None,
    )
    value: Optional[Decimal] = Field(examples=[Decimal("34.70")], default=None)
    tolerance: Optional[W24PropertyAbbeToleranceType] = Field(default=None)


class W24PropertyAbbeValueFreeText(W24PropertyAbbeValue):
    """Abbe Value Free Text"""

    free_text: str
    variation_type: Literal["FREETEXT"] = "FREETEXT"


W24PropertyAbbeValueType = Union[
    W24PropertyAbbeValueNumberValue,
    W24PropertyAbbeValueFreeText,
]
