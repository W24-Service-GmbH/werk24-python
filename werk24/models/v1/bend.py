from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import Field

from .angle import W24AngleSize
from .base_feature import W24BaseFeatureModel
from .size import W24Size, W24SizeNominal
from .tolerance import W24ToleranceGeneral, W24ToleranceType


class W24BendDirection(str, Enum):
    """
    Direction of the bend.
    """

    UP = "UP"
    DOWN = "DOWN"
    LEFT = "LEFT"
    RIGHT = "RIGHT"


class W24BendType(str, Enum):
    CENTER_LINE_BEND = "CLB"
    INNER_MOLD_BEND = "IMB"
    OUTER_MOLD_BEND = "OMB"


class W24BendLabel(W24BaseFeatureModel):
    """
    Bend feature extracted from the drawing.
    """

    blurb: str = Field(
        description="Human readable description of the bend.",
        examples=["BEND: UP 90° R5 CLB"],
    )

    quantity: Optional[int] = Field(
        gt=0, description="Quantity of the bend.", examples=[1], default=1
    )

    bend_type: Optional[W24BendType] = Field(
        description="Type of the bend line according to DIN6935. No default value can be provided as practices differ across industries.",
        examples=[W24BendType.CENTER_LINE_BEND],
    )

    angle: Optional[W24AngleSize] = Field(
        description="Angle of the bend in degrees, must be between 0 and 360.",
        examples=[W24AngleSize(angle=Decimal("90"), blurb="90°")],
    )

    radius: Optional[W24Size] = Field(
        description="Radius of the bend.",
        examples=[W24SizeNominal(blurb="5", nominal_size=Decimal("5"))],
    )

    radius_tolerance: W24ToleranceType = Field(
        description="Tolerance of the radius. If no tolerance is given, the general tolerance applies.",
        default=W24ToleranceGeneral(),
    )

    direction: Optional[W24BendDirection] = Field(
        description="Direction of the bend (up or down).",
        examples=[W24BendDirection.UP],
    )
