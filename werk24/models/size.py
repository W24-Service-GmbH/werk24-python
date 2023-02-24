import abc
from decimal import Decimal
from enum import Enum
from typing import Literal, Optional, Union

from pydantic import BaseModel, Field
from typing_extensions import Annotated

from .general_tolerances import W24GeneralTolerancesStandard


class W24SizeToleranceParent(BaseModel, abc.ABC):
    """Abstract Base Class to cover the Tolerances.

    Attributes:
        blurb (str): String representation for human consumption
    """
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


class W24SizeToleranceFitsizeISO(W24SizeToleranceParent):
    """ISO fit size tolerances.

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
    toleration_type: Literal["FIT_SIZE_ISO"] = "FIT_SIZE_ISO"
    blurb: str
    deviation_lower: Decimal
    deviation_upper: Decimal
    fundamental_deviation: str
    tolerance_grade: W24ToleranceGrade

    @property
    def deviation_width(self) -> Decimal:
        """ Deviation Width

        Returns:
            Decimal: Deviation width
        """
        return self.deviation_upper-self.deviation_lower


class W24SizeToleranceReference(W24SizeToleranceParent):
    """ Measures written in brackets are Reference
    Measures that are not tolerated.

    Attributes:
        tolerantion_type (W24SizeToleranceType): Reference
            Tolerance Type

        blurb (str): Text representation for human consumption.
    """
    toleration_type: Literal["REFERENCE"] = "REFERENCE"


class W24SizeToleranceOffSize(W24SizeToleranceParent):
    """ Off-size based tolerances

    Attributes:
        blurb (str): Text representation for human consumption.

        deviation_lower (Decimal): Lower deviation from the
            nominal size

        deviation_upper (Decimal): Upper deviation from the
            nominal size

        tolerance_grade (int): Tolerance Grade corresponding to
            ISO 286-1. In German IT-Grad.
    """
    toleration_type: Literal["OFF_SIZE"] = "OFF_SIZE"
    deviation_lower: Decimal
    deviation_upper: Decimal
    tolerance_grade: W24ToleranceGrade


class W24SizeToleranceGeneral(W24SizeToleranceParent):
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
    toleration_type: Literal["GENERAL_TOLERANCES"] = "GENERAL_TOLERANCES"
    blurb: str = ""
    standard: Optional[W24GeneralTolerancesStandard]
    standard_class: Optional[str]
    deviation_lower: Optional[Decimal]
    deviation_upper: Optional[Decimal]
    tolerance_grade: Optional[W24ToleranceGrade]


class W24SizeToleranceTheoreticallyExact(W24SizeToleranceParent):
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
    toleration_type: Literal["THEORETICALLY_EXACT"] = "THEORETICALLY_EXACT"


class W24SizeToleranceMinimum(W24SizeToleranceParent):
    """ Minimum Size of a measure
    Example:
        min. 15
    """
    toleration_type: Literal["MINIMUM"] = "MINIMUM"


class W24SizeToleranceMaximum(W24SizeToleranceParent):
    """ Maximum Size of a measure
    Example:
        max 15
    """
    toleration_type: Literal["MAXIMUM"] = "MAXIMUM"


class W24SizeToleranceApproximation(W24SizeToleranceParent):
    """ Approximation of a measure
    Example:
        ~ 15
        ca. 14
    """
    toleration_type: Literal["APPROXIMATION"] = "APPROXIMATION"


W24Tolerance = Annotated[
    Union[
        W24SizeToleranceFitsizeISO,
        W24SizeToleranceOffSize,
        W24SizeToleranceReference,
        W24SizeToleranceGeneral,
        W24SizeToleranceTheoreticallyExact,
        W24SizeToleranceMinimum,
        W24SizeToleranceMaximum,
        W24SizeToleranceApproximation
    ],
    Field(discriminator='toleration_type')
]


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
        width_across_flats: Size across flats
            aka. wrench size.
    """
    size_type = W24SizeType.WIDTH_ACROSS_FLATS

    width_across_flats: Decimal
