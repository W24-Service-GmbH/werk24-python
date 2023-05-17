from enum import Enum
from pydantic import BaseModel

from werk24.models.fraction import W24Fraction


class W24ViewType(str, Enum):
    """An enumeration of view types.
    """
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
    scale (W24Fraction): The scale of the view, a fraction represented
        by the W24Fraction model.
    """
    view_type: W24ViewType
    blurb: str
    scale: W24Fraction
