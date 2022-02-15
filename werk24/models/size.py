import abc
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel

from .general_tolerances import W24GeneralTolerancesStandard


class W24SizeToleranceType(str, Enum):
    """ Enum of the supported tolerations
    """
    APPROXIMATION = "APPROXIMATION"
    FIT_SIZE_ISO = "FIT_SIZE_ISO"
    GENERAL_TOLERANCES = "GENERAL_TOLERANCES"
    MINIMUM = "MINIMUM"
    MAXIMUM = "MAXIMUM"
    OFF_SIZE = "OFF_SIZE"
    THEORETICALLY_EXACT = "THEORETICALLY_EXACT"
    REFERENCE = "REFERENCE"


class W24SizeTolerance(BaseModel, abc.ABC):
    """ Abstract Base Class to cover the Tolerations

    Attributes:
        blurb (str): String representation for human consumption

        toleration_type (W24SizeToleranceType):  Toleration Type for
            deserialization
    """

    toleration_type: W24SizeToleranceType

    blurb: str


class W24ToleranceGradeWarning(str, Enum):
    """ Warnings associated with the Tolerance Grade.
    """

    SIZE_LARGER_THAN_NORM = "SIZE_LARGER_THAN_NORM"
    TOLERANCE_WIDTH_SMALLER_THAN_NORM = "TOLERANCE_WIDTH_SMALLER_THAN_NORM"
    TOLERANCE_WIDTH_LARGER_THAN_NORM = "TOLERANCE_WIDTH_LARGER_THAN_NORM"


class W24ToleranceGrade(BaseModel):
    """ Tolerance Grade following ISO 286-1

    Attributes:
        blurb (Optional[str]): Blurb for human consumption.

        grade (Optional[str]): Tolerance Grade in the range
            of IT01 to IT18. None if the tolerance is outside the
            normed region

        warning (Optional[W24ToleranceGradeWarning]): the norm is
            limited to the size range (0 - 3150mm) and the
            tolerance range of IT1 - IT18. When we reach the
            ends of this norm, we return a warning.

        NOTE: when a tolerance is outside the norm, we still
            return the closest matching grade.

        NOTE: when tolerances are implausible (e.g., 3+/-6),
            Werk24 will strip the tolerance completely and
            return an untolerated measure of nominal size 3.

    """
    blurb: str

    grade: Optional[str]

    warning: Optional[W24ToleranceGradeWarning]


class W24SizeToleranceFitsizeISO(W24SizeTolerance):
    """ ISO fit size tolerations

    Attributes:
        blurb (str): Text representation for human consumption.

        deviation_lower (Decimal): Lower deviation from the
            nominal size

        deviation_upper (Decimal): Upper deviation from the
            nominal size

        fundamental_deviation (str): Fundamental deviation of
            the fit (e.g., 'H' for a 'H7' fit)

        tolerance_grade (Optional[int]): Tolerance Grade corresponding
            to ISO 286-1. In German IT-Grad.
    """
    toleration_type = W24SizeToleranceType.FIT_SIZE_ISO

    blurb: str

    deviation_lower: Decimal

    deviation_upper: Decimal

    fundamental_deviation: str

    tolerance_grade: W24ToleranceGrade


class W24SizeToleranceReference(W24SizeTolerance):
    """ Measures written in brackets are Reference
    Measures that are not tolerated.

    Attributes:
        tolerantion_type (W24SizeToleranceType): Reference
            Tolerance Type

        blurb (str): Text representation for human consumption.
    """
    toleration_type = W24SizeToleranceType.REFERENCE

    blurb: str


class W24SizeToleranceOffSize(W24SizeTolerance):
    """ Off-size based tolerations

    Attributes:
        blurb (str): Text representation for human consumption.

        deviation_lower (Decimal): Lower deviation from the
            nominal size

        deviation_upper (Decimal): Upper deviation from the
            nominal size

        tolerance_grade (int): Tolerance Grade corresponding to
            ISO 286-1. In German IT-Grad.
    """
    toleration_type = W24SizeToleranceType.OFF_SIZE

    deviation_lower: Decimal

    deviation_upper: Decimal

    tolerance_grade: W24ToleranceGrade


class W24SizeToleranceGeneral(W24SizeTolerance):
    """ General Tolerances

    Attributes:
        tolerance_type: W24SizeToleranceType General Tolerances
            as key to differentiate between the different
            tolerance types

        blurb: Blurb of the General Tolerance following the
            pattern of W24ToleranceOffSize

        standard: GeneralToleranceStandard that is specified in
            the TitleBlock. If the TitleBlock is not requested
            of it no GeneralTolerance was found, this is set to
            None.

        standard_class: GeneralTolerance Class if known. None
            otherwise.

        deviation_lower: Lower deviation from the nominal size
            if the General Tolerance is known. None otherwise.

        deviation_upper: Upper deviation from the nominal size
            if the General Tolerance is known. None otherwise.

        tolerance_grade (int): Tolerance Grade corresponding to
            ISO 286-1. (German: IT-Grad).
    """
    toleration_type = W24SizeToleranceType.GENERAL_TOLERANCES

    blurb: str = ""

    standard: Optional[W24GeneralTolerancesStandard]

    standard_class: Optional[str]

    deviation_lower: Optional[Decimal]

    deviation_upper: Optional[Decimal]

    tolerance_grade: Optional[W24ToleranceGrade]


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
    WIDTH_ACROSS_FLATS = "WIDTHS_ACCROSS_FLATS"


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
        width_accross_flats: Size accross flats
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
