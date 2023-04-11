import abc
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel


class W24SizeType(str, Enum):
    """ Enum describing the different size types
    """
    NOMINAL = "NOMINAL"
    DIAMETER = "DIAMETER"
    WIDTH_ACROSS_FLATS = "WIDTHS_ACROSS_FLATS"


class W24Size(BaseModel, abc.ABC):
    """ Abstract Base Class for the Sizes

    Attributes:
        blurb: Blurb for human consumption

        size_type: Size type for deserialization

        nominal_size: Unit-less nominal size. The unit
            is it attached to the parent object, that
            also defines the toleration.
    """
    blurb: str
    size_type: W24SizeType
    nominal_size: Decimal


class W24SizeNominal(W24Size):
    """ Exactly your nominal size
    """
    size_type = W24SizeType.NOMINAL


class W24SizeDiameter(W24Size):
    """ Diameter size
    """
    size_type = W24SizeType.DIAMETER


class W24SizeWidthsAcrossFlats(W24Size):
    """ Width across flats / Wrench Sizes

    Attributes:
        width_across_flats: Size across flats
            aka. wrench size.
    """
    size_type = W24SizeType.WIDTH_ACROSS_FLATS

    width_across_flats: Decimal
