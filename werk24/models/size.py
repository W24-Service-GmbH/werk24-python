import abc
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel
from werk24.models.unit import W24UnitLength


class W24SizeType(str, Enum):
    """
    Enumeration class for W24 size types.

    Attributes:
    ----------
    NOMINAL (str): Nominal size type.
    DIAMETER (str): Diameter size type.
    WIDTH_ACROSS_FLATS (str): Width across flats size type.
    """

    NOMINAL = "NOMINAL"
    DIAMETER = "DIAMETER"
    SPHERICAL_DIAMETER = "SPHERICAL_DIAMETER"
    WIDTH_ACROSS_FLATS = "WIDTHS_ACROSS_FLATS"
    SQUARE = "SQUARE"


class W24Size(BaseModel, abc.ABC):
    """
    Abstract Base Class for the Sizes.

    Attributes:
    ----------
    blurb: A blurb for human consumption.

    size_type: The type of size for deserialization.

    nominal_size: The unit-less nominal size.
        The unit is attached to the parent
        object, which also defines the toleration.

    unit: Unit of the measure if known. This
        should typically be inch or millimeter.
        In some cases it might be possible that
        the units are unknown.
    """

    blurb: str
    size_type: W24SizeType
    nominal_size: Decimal
    unit: Optional[W24UnitLength] = None


class W24SizeNominal(W24Size):
    """
    Nominal size for a W24Size.
    """

    size_type: W24SizeType = W24SizeType.NOMINAL


class W24SizeSphericalDiameter(W24Size):
    """
    Spherical Diameter size for a W24Size.
    """

    size_type: W24SizeType = W24SizeType.SPHERICAL_DIAMETER


class W24SizeDiameter(W24Size):
    """
    Diameter size for a W24Size.
    """

    size_type: W24SizeType = W24SizeType.DIAMETER


class W24SizeSquare(W24Size):
    """
    Square size for a W24Size.
    """

    size_type: W24SizeType = W24SizeType.SQUARE


class W24SizeWidthsAcrossFlats(W24Size):
    """
    Width across flats / Wrench Sizes.

    Attributes:
    ----------
    width_across_flats: Size across flats
        aka. wrench size.
    """

    size_type: W24SizeType = W24SizeType.WIDTH_ACROSS_FLATS

    width_across_flats: Decimal
