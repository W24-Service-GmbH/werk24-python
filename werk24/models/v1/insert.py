from enum import Enum

from pydantic import BaseModel, Field


class W24InsertType(str, Enum):
    ALIGNMENT = "ALIGNMENT"
    SEALING = "SEALING"
    THREAD = "THREAD"
    WEAR = "WEAR"
    WELDING = "WELDING"


class W24Insert(BaseModel):
    blurb: str = Field(..., description="Descriptive name of the insert")
    category: W24InsertType = Field(..., description="Category of the insert")
