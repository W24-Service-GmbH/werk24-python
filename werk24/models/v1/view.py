from enum import Enum
from typing import Optional

from pydantic import BaseModel

from .fraction import W24Fraction


class W24ViewType(str, Enum):
    """An enumeration of view types."""

    VIEW = "VIEW"
    SECTIONAL = "SECTIONAL"
    DETAIL = "DETAIL"
    ISOMETRIC = "ISOMETRIC"


class W24View(BaseModel):
    """Representation of a View Name

    Attributes:
    ----------
    view_type (W24ViewType): The view type, an enumeration member.
    blurb (str): The blurb of the view, a string.
    name (str): Name of the view
    scale (W24Fraction): The scale of the view, a fraction represented
        by the W24Fraction model.
    """

    view_type: W24ViewType
    blurb: str
    name: str
    scale: Optional[W24Fraction]
