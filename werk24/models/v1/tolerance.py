from decimal import Decimal
from enum import Enum
from typing import Optional, Union

from pydantic import BaseModel

from .base_feature import W24BaseFeatureModel
from .gender import W24Gender
from .standard import W24Standard
from .typed_model import W24TypedModel


class W24Tolerance(W24TypedModel):
    """Abstract Base Class to cover the Tolerances.

    Attributes:
        blurb (str): String representation for human consumption

        toleration_type (W24SizeToleranceType):  Toleration Type for
            deserialization
    """

    class Config:
        discriminators = ("toleration_type",)

    blurb: str
    toleration_type: str


class W24ToleranceGradeWarning(str, Enum):
    """Warnings associated with the Tolerance Grade."""

    SIZE_LARGER_THAN_NORM = "SIZE_LARGER_THAN_NORM"
    TOLERANCE_WIDTH_SMALLER_THAN_NORM = "TOLERANCE_WIDTH_SMALLER_THAN_NORM"
    TOLERANCE_WIDTH_LARGER_THAN_NORM = "TOLERANCE_WIDTH_LARGER_THAN_NORM"


class W24ToleranceGrade(BaseModel):
    """Tolerance Grade following ISO 286-1

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
            return an untoleranced measure of nominal size 3.

    """

    blurb: str

    grade: Optional[str]

    warning: Optional[W24ToleranceGradeWarning]


class W24ToleranceFitsizeISO(W24Tolerance):
    """ISO fit size tolerances

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

    toleration_type: str = "FIT_SIZE_ISO"

    deviation_lower: Decimal

    deviation_upper: Decimal

    fundamental_deviation: str

    tolerance_grade: W24ToleranceGrade

    @property
    def deviation_width(self) -> Decimal:
        """Deviation Width

        Returns:
            Decimal: Deviation width
        """
        return self.deviation_upper - self.deviation_lower


class W24ToleranceReference(W24Tolerance):
    """Measures written in brackets are Reference."""

    toleration_type: str = "REFERENCE"


class W24ToleranceOffSize(W24Tolerance):
    """Off-size based tolerances

    Attributes:
        blurb (str): Text representation for human consumption.

        deviation_lower (Decimal): Lower deviation from the
            nominal size

        deviation_upper (Decimal): Upper deviation from the
            nominal size

        tolerance_grade (int): Tolerance Grade corresponding to
            ISO 286-1. In German IT-Grad.
    """

    toleration_type: str = "OFF_SIZE"
    deviation_lower: Decimal
    deviation_upper: Decimal
    tolerance_grade: W24ToleranceGrade


class W24ToleranceGeneral(W24Tolerance):
    """General Tolerances

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

    toleration_type: str = "GENERAL_TOLERANCES"
    blurb: str = ""
    standard: Optional[W24Standard] = None
    standard_class: Optional[str] = None
    deviation_lower: Optional[Decimal] = None
    deviation_upper: Optional[Decimal] = None
    tolerance_grade: Optional[W24ToleranceGrade] = None


class W24ToleranceTheoreticallyExact(W24Tolerance):
    """Theoretically Exact Measures after ISO 5458
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

    toleration_type: str = "THEORETICALLY_EXACT"


class W24ToleranceMinimum(W24Tolerance):
    """Minimum Size of a measure
    Example:
        min. 15
    """

    toleration_type: str = "MINIMUM"


class W24ToleranceMaximum(W24Tolerance):
    """Maximum Size of a measure
    Example:
        max 15
    """

    toleration_type: str = "MAXIMUM"


class W24ToleranceApproximation(W24Tolerance):
    """Approximation of a measure
    Example:
        ~ 15
        ca. 14
    """

    toleration_type: str = "APPROXIMATION"


class W24ToleranceFeature(W24BaseFeatureModel):
    """Characterization of a Tolerance Feature.

    Attributes:
        gender: Gender (male or female) of the tolerance feature.
            This is determined by checking whether the tolerance feature is
            located on the outer contour of the part or inside the part.
            When the outer contour is unavailable (e.g., in detail drawings),
            the gender is set to None.

        length: Length of the slug corresponding to the tolerance feature.

    """

    gender: Optional[W24Gender]

    length: Optional[Decimal]

    tolerance: W24Tolerance


W24ToleranceType = Union[
    W24ToleranceApproximation,
    W24ToleranceFitsizeISO,
    W24ToleranceGeneral,
    W24ToleranceMaximum,
    W24ToleranceMinimum,
    W24ToleranceOffSize,
    W24ToleranceReference,
    W24ToleranceTheoreticallyExact,
]
