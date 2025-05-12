from decimal import Decimal
from typing import Any, Literal, Optional, Union

from pydantic import BaseModel, Field

from ..property.base import W24Property
from ..property.fraunhofer import W24FraunhoferLine
from ..typed_model import W24TypedModel


class W24PropertyRefractiveTolerance(W24TypedModel):
    class Config:
        discriminators = ("refractive_tolerance_type",)

    refractive_tolerance_type: Any


class W24PropertyRefractiveToleranceValue(W24PropertyRefractiveTolerance):
    refractive_tolerance_type: Literal["VALUE"] = "VALUE"
    blurb: str = Field(examples=["±0.0005"])
    deviation_upper: Optional[Decimal] = Field(
        examples=[Decimal("0.0005")], default=None
    )
    deviation_lower: Optional[Decimal] = Field(
        examples=[Decimal("-0.0005")], default=None
    )


class W24PropertyRefractiveToleranceStep(W24PropertyRefractiveTolerance):
    refractive_tolerance_type: Literal["STEP"] = "STEP"
    blurb: str = Field(examples=["Step 3", "Step 0.5"])
    step: Decimal = Field(examples=[Decimal("3"), Decimal("0.5")])


W24PropertyRefractiveToleranceType = Union[
    W24PropertyRefractiveToleranceValue, W24PropertyRefractiveToleranceStep
]


class W24PropertyRefractiveVariation(BaseModel):
    class Config:
        discriminators = ("variation_type",)

    variation_type: Any


class W24PropertyRefractiveVariationSchottGrade(W24PropertyRefractiveVariation):
    """Refractive Variation Schott Grade"""

    variation_type: Literal["SCHOTT_GRADE"] = "SCHOTT_GRADE"
    blurb: str = Field(examples=("LN", "LH1", "LH2"))
    grade: str = Field(examples=["LN", "LH1", "LH2"])


class W24PropertyRefractiveVariationIso12123(W24PropertyRefractiveVariation):
    """Refractive Variation ISO 12123"""

    variation_type: Literal["ISO_12123"] = "ISO_12123"
    blurb: str = Field(examples=("NV20", "NV10", "NV05"))
    grade: str = Field(examples=["NV20", "NV10", "NV05"])


class W24PropertyRefractiveVariationFreeText(W24PropertyRefractiveVariation):
    """Refractive Variation Free Text"""

    free_text: str
    variation_type: Literal["FREETEXT"] = "FREETEXT"


W24PropertyRefractiveVariationType = Union[
    W24PropertyRefractiveVariationSchottGrade,
    W24PropertyRefractiveVariationIso12123,
    W24PropertyRefractiveVariationFreeText,
]


class W24PropertyRefractiveIndex(W24Property):
    """Parent for all Refractive Index"""

    property_type: Literal["REFRACTIVE_INDEX"] = "REFRACTIVE_INDEX"


class W24PropertyRefractiveIndexValue(W24PropertyRefractiveIndex):
    """Refractive Index Value"""

    property_subtype: Literal["VALUE"] = "VALUE"

    blurb: str = Field(
        examples=[
            "nd = 1.72047 ±0.0005",
            "ne = 1.57487 ±0.0005",
        ]
    )

    line: Optional[W24FraunhoferLine] = Field(
        examples=[
            W24FraunhoferLine.D_LINE,
            W24FraunhoferLine.E_LINE,
        ],
        default=None,
    )
    value: Decimal = Field(examples=[Decimal("1.72047")])
    tolerance: Optional[W24PropertyRefractiveToleranceType] = Field(default=None)
    variation: Optional[W24PropertyRefractiveVariationType] = Field(
        examples=[
            W24PropertyRefractiveVariationSchottGrade(blurb="NV20", grade="NV20")
        ],
        default=None,
    )


class W24PropertyRefractiveIndexFreeText(W24PropertyRefractiveIndex):
    """Refractive Index Free Text"""

    free_text: str
    variation_type: Literal["FREETEXT"] = "FREETEXT"


W24PropertyRefractiveIndexType = Union[
    W24PropertyRefractiveIndexValue,
    W24PropertyRefractiveIndexFreeText,
]
