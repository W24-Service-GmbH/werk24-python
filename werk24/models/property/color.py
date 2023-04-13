from typing import Literal

from werk24.models.property.base import W24Property


class W24PropertyColor(W24Property):
    """Color Property.

    NOTE: at this stage we do not make
        the colors comparable. There
        might be ways of doing this, but
        colors are complex and most
        color systems cannot express the
        complete space (e.g., RGB is not
        describing the glossiness of the
        color).
    """
    property_type: Literal["COLOR"] = "COLOR"


class W24PropertyColorRAL(W24PropertyColor):
    """Color Property as RAL number.

    Attributes:
        ral_number (str): RAL number of the
            color. Note that there are three
            different RAL numbering systems
            in use.
    """
    property_subtype: Literal["RAL"] = "RAL"
    ral_number: str


class W24PropertyColorBlurb(W24PropertyColor):
    """Color Property as Blurb.

    Attributes:
        color_name (str): English Color name.
            See Documentation for full list of
            supported colors.
    """
    property_subtype: Literal["BLURB"] = "BLURB"
    color_name: str
