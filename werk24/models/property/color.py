from enum import Enum
from typing import Literal

from werk24.models.property.base import W24Property


class W24PropertyColorType(str, Enum):
    BLURB = "BLURB"
    RAL = "RAL"


class W24PropertyColor(W24Property):
    """Meta Data for Color.

    NOTE: at this stage we do not make
        the colors comparable. There
        might be ways of doing this, but
        colors are complex and most
        color systems cannot express the
        complete space (e.g., RGB is not
        describing the glossiness of the
        color).
    """
    type: Literal["COLOR"] = "COLOR"
    color_type: W24PropertyColorType
    color: str
