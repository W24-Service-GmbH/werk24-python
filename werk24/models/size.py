import abc
from typing import Dict, Any, Optional
from enum import Enum

from pydantic import BaseModel


class W24SizeToleranceType(str, Enum):
    """ Enum of the supported tolerances
    """
    APPROXIMATION = "APPROXIMATION"
    FIT_SIZE_ISO = "FIT_SIZE_ISO"
    GENERAL_TOLERANCES = "GENERAL_TOLERANCES"
    MINIMUM = "MINIMUM"
    MAXIMUM = "MAXIUM"
    OFF_SIZE = "OFF_SIZE"
    THEORETICALLY_EXACT = "THEORETICALLY_EXACT"


class W24SizeTolerance(BaseModel, abc.ABC):
    """ Abstract Base Class to cover the Tolerations
    """

    toleration_type: W24SizeToleranceType
    """ Toleration Type for deserialization
    """

    blurb: str
    """ String representation for human consumption
    """


class W24SizeToleranceFitsizeISO(W24SizeTolerance):
    """ ISO fit size tolerations
    """
    toleration_type = W24SizeToleranceType.FIT_SIZE_ISO

    blurb: str
    """ uninterpreted string representation of the fit size
    """

    deviation_lower: float
    """ Lower deviation from the nominal size
    """

    deviation_upper: float
    """ Upper deviation from the nominal size
    """


class W24SizeToleranceOffSize(W24SizeTolerance):
    """ Off-size based tolerations
    """
    toleration_type = W24SizeToleranceType.OFF_SIZE

    deviation_lower: float
    """ Lower deviation from the nominal size
    """

    deviation_upper: float
    """ Upper deviation from the nominal size
    """


class W24SizeToleranceGeneral(W24SizeTolerance):
    """ General Tolerances
    """
    toleration_type = W24SizeToleranceType.GENERAL_TOLERANCES

    blurb = ""
    """ Set the blub to '' (default for General Tolerances)
    """


class W24SizeToleranceTheoreticallyExact(W24SizeTolerance):
    """ Theoretically Exact Measures after ISO 5458
    must not be tolerated. They are indicated by a small
    rectangular frame.

    Example:
        +------+
        |  15  |
        +------+

    !!! note
        In practice, we see Technical drawings contain
        tolerated, theoretically exact measures.
        Example:
            +------------+
            | 15 +/- 0.2 |
            +------------+
        In these situations the toleration takes priority.
    """
    toleration_type = W24SizeToleranceType.THEORETICALLY_EXACT


class W24SizeToleranceMinimum(W24SizeTolerance):
    """ Minimum Size of a measure
    Example:
        min. 15
    """

    toleration_type = W24SizeToleranceType.MINIMUM


class W24SizeToleranceMaximum(W24SizeTolerance):
    """ Maximum Size of a measure
    Example:
        max 15
    """

    toleration_type = W24SizeToleranceType.MAXIMUM


class W24SizeToleranceApproximation(W24SizeTolerance):
    """ Approximation of a measure
    Example:
        ~ 15
        ca. 14
    """
    toleration_type = W24SizeToleranceType.APPROXIMATION


class W24SizeType(str, Enum):
    """ Enum describing the different size types
    """
    NOMINAL = "NOMINAL"
    DIAMETER = "DIAMETER"
    WIDTHS_ACCROSS_FLATS = "WIDTHS_ACCROSS_FLATS"


class W24Size(BaseModel, abc.ABC):
    """ Abstract Base Class for the Sizes

    Attributes:
        blurb: Blurb for human consumption

        size_type: Size type for deserialization

        nominal_size: Unitless nominal size. The unit
            is it attached to the parent object, that
            also defines the toleration.
    """
    blurb: str

    size_type: W24SizeType

    nominal_size: float


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

    Attributes:
        width_accross_flats: Size accross flats
            aka. wrench size.
    """
    size_type = W24SizeType.WIDTHS_ACCROSS_FLATS

    width_accross_flats: float


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
        W24SizeToleranceType.OFF_SIZE: W24SizeToleranceOffSize,
        W24SizeToleranceType.MINIMUM: W24SizeToleranceMinimum,
        W24SizeToleranceType.MAXIMUM: W24SizeToleranceMaximum,

        W24SizeToleranceType.THEORETICALLY_EXACT:
        W24SizeToleranceTheoreticallyExact,
    }.get(type_)

    if type_ is None:
        return None

    return class_.parse_obj(raw)
