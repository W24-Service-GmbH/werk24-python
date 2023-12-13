from decimal import Decimal
from typing import Any, Literal, Optional, Union

from pydantic import Field

from werk24.models.property.base import W24Property
from werk24.models.property.fraunhofer import W24FraunhoferLine
from werk24.models.typed_model import W24TypedModel


class W24PropertyAbbeTolerance(W24TypedModel):
    class Config:
        discriminators = ("abbe_tolerance_type",)

    blurb: str
    abbe_tolerance_type: Any


class W24PropertyAbbeToleranceValue(W24PropertyAbbeTolerance):
    abbe_tolerance_type: Literal["VALUE"] = "VALUE"
    blurb: str = Field(examples=["±0.8%"])
    deviation_upper: Optional[Decimal] = Field(examples=[Decimal("0.8")])
    deviation_lower: Optional[Decimal] = Field(examples=[Decimal("-0.8")])


class W24PropertyAbbeToleranceStep(W24PropertyAbbeTolerance):
    abbe_tolerance_type: Literal["STEP"] = "STEP"
    blurb: str = Field(examples=["Step 3", "Step 0.5"])
    step: Decimal = Field(examples=[Decimal("3"), Decimal("0.5")])


W24PropertyAbbeToleranceType = Union[
    W24PropertyAbbeToleranceValue, W24PropertyAbbeToleranceStep
]


class W24PropertyAbbeValue(W24Property):
    property_type: Literal["ABBE_NUMBER"] = "ABBE_NUMBER"


class W24PropertyAbbeValueNumberValue(W24PropertyAbbeValue):
    property_subtype: Literal["VALUE"] = "VALUE"

    blurb: str = Field(examples=["vd = 34.70 ±0.8%", "ve = 57.27 ±0.5%"])

    line: Optional[W24FraunhoferLine] = Field(
        examples=[
            W24FraunhoferLine.D_LINE,
            W24FraunhoferLine.E_LINE,
        ],
    )
    value: Optional[Decimal] = Field(examples=[Decimal("34.70")])
    tolerance: Optional[W24PropertyAbbeToleranceType]


W24PropertyAbbeValueType = W24PropertyAbbeValueNumberValue
