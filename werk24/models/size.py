import abc
from enum import Enum
from pydantic import BaseModel


class W24SizeType(str, Enum):
    NOMINAL = "NOMINAL"
    DIAMETER = "DIAMETER"
    WIDTHS_ACCROSS_FLATS = "WIDTHS_ACCROSS_FLATS"


class W24Size(BaseModel, abc.ABC):
    """ Abstract Base Class for the Sizes
    """

    blurb: str
    """ blurb for human consumption
    """

    size_type: W24SizeType
    """ size type for deserialization
    """

    nominal_size: float
    """ Nominal size
    """


class W24SizeNominal(W24Size):
    """ Exactly your nominal size
    """
    size_type = W24SizeType.NOMINAL


class W24SizeDiameter(W24Size):
    """ Diameter size
    """
    size_type = W24SizeType.DIAMETER


class W24SizeWidthsAcrossFlats(W24Size):
    """ Widths accross flats / Wrench Sizes
    """
    size_type = W24SizeType.WIDTHS_ACCROSS_FLATS

    width_accross_flats: float
    """ Size accross flats or Wrench sizes
    """
