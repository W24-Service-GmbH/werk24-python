"""Structured quality designations for thermally cut edges."""

from typing import Literal, Optional

from pydantic import BaseModel, Field


class ThermalCutQuality(BaseModel):
    """ISO 9013 designation as written on the drawing.

    The three digits describe the perpendicularity/angularity tolerance range,
    the mean profile height Rz5 range, and the tolerance class, respectively.
    Missing digits remain null; no quality value is inferred from the standard
    alone. These are designation numbers, not dimensional tolerances.
    """

    standard: Literal["ISO 9013"] = "ISO 9013"
    perpendicularity_range: Optional[int] = Field(
        None, ge=0, le=9,
        description="First designation digit: perpendicularity/angularity tolerance range.",
    )
    rz5_range: Optional[int] = Field(
        None, ge=0, le=9,
        description="Second designation digit: mean profile height Rz5 range.",
    )
    tolerance_class: Optional[int] = Field(
        None, ge=0, le=9,
        description="Third designation digit: tolerance class.",
    )
