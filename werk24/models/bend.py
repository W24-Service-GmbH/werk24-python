from typing import Optional
from decimal import Decimal
from pydantic import Field
from enum import Enum
from .base_feature import W24BaseFeatureModel

class W24BendDirection(str, Enum):
    """
    Direction of the bend.
    """
    UP = "UP"
    DOWN = "DOWN"

class W24Bend(W24BaseFeatureModel):
    """
    Bend feature extracted from the drawing.
    """

    angle: Optional[Decimal] = Field(
        gt=0, 
        lt=360, 
        description="Angle of the bend in degrees, must be between 0 and 360.",
        examples=[Decimal("90")]
    )
    
    radius: Optional[Decimal] = Field(
        gt=0, 
        description="Radius of the bend.",
        examples=[Decimal("5")]
    )

    direction: Optional[W24BendDirection] = Field(
        description="Direction of the bend (up or down).",
        examples=[W24BendDirection.UP]
    )
