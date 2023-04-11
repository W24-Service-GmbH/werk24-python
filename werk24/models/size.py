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


def parse_tolerance(
    raw: Dict[str, Any]
) -> Optional[W24SizeTolerance]:
    """ Pydantic does not automatically return the correct
    W24SizeTolerance object. This function looks at the toleration_type
    attribute and returns the correct W24SizeTolerance subclass

    Args:
        size_tolerance_raw (Dict[str, str]): Raw Dictionary of
            the size tolerance

    Returns:
        W24SizeTolerance: Correctly deserialized Size Tolerance
    """
    # get the class in question
    type_ = raw.toleration_type \
        if hasattr(raw, 'toleration_type')\
        else raw.get('toleration_type')

    class_ = {
        W24SizeToleranceType.APPROXIMATION: W24SizeToleranceApproximation,
        W24SizeToleranceType.FIT_SIZE_ISO: W24SizeToleranceFitsizeISO,
        W24SizeToleranceType.GENERAL_TOLERANCES: W24SizeToleranceGeneral,
        W24SizeToleranceType.MINIMUM: W24SizeToleranceMinimum,
        W24SizeToleranceType.MAXIMUM: W24SizeToleranceMaximum,
        W24SizeToleranceType.OFF_SIZE: W24SizeToleranceOffSize,
        W24SizeToleranceType.REFERENCE: W24SizeToleranceReference,
        W24SizeToleranceType.THEORETICALLY_EXACT:
        W24SizeToleranceTheoreticallyExact,
    }.get(type_)

    if class_ is None:
        return None

    return class_.parse_obj(raw)
