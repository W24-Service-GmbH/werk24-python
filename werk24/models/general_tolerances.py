from decimal import Decimal
from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel, validator

from werk24.models.unit import W24UnitLength

from .base_feature import W24BaseFeatureModel


class W24GeneralTolerancesStandard(str, Enum):
    """Enum of all supported
    General Tolerance Standards
    """

    DIN_7168 = "DIN 7168"
    ISO_2768 = "ISO 2768"
    ISO_4759_1 = "ISO 4759-1"
    TOLERANCE_NOTE = "TOLERANCE_NOTE"


class W24ToleranceProperty(str, Enum):
    """Enum of all attributes that can
    be described by general tolerances
    """

    ANGULAR = "ANGULAR"
    FLATNESS = "FLATNESS"
    LINEAR = "LINEAR"
    PERPENDICULARITY = "PERPENDICULARITY"
    RADIUS = "RADIUS"
    RUNOUT = "RUNOUT"
    STRAIGHTNESS = "STRAIGHTNESS"
    SYMMETRY = "SYMMETRY"


class W24GeneralTolerancesPrinciple(str, Enum):
    """Enum of the supported General Tolerance
    Principles.
    """

    INDEPENDENCE = "INDEPENDENCE"
    ENVELOPE = "ENVELOPE"


class W24IntervalEnd(str, Enum):
    """
    Enum for handling the interval ends.
    Open for  `<`
    Close for `<=`
    """

    OPEN = "OPEN"
    CLOSE = "CLOSE"


class W24ToleranceTableItem(BaseModel):
    """
    Tolerance Table Item.

    Attributes:
        nominal_min: Lower bound of the nominal value
        nominal_min_end: Interval end of the lower bound
        nominal_max: Upper bound of the nominal value
        nominal_max_end: Interval end of the upper bound
        decimal_places: Number of decimal places. This is
            required for US-type tolerances.
        deviation_min: Lower bound of the deviation
        deviation_max: Upper bound of the deviation
    """

    nominal_min: Optional[Decimal]
    nominal_min_end: W24IntervalEnd = W24IntervalEnd.OPEN
    nominal_max: Optional[Decimal]
    nominal_max_end: W24IntervalEnd = W24IntervalEnd.CLOSE

    decimal_places: Optional[int] = None

    deviation_min: Optional[Decimal]
    deviation_max: Optional[Decimal]

    unit: Optional[W24UnitLength] = None

    @validator("nominal_min", pre=True)
    def nominal_min_validator(  # NOQA
        cls, raw: Union[str, float, None]
    ) -> Optional[Decimal]:
        """Ensure the proper conversion of the the
        Decimal value
        """
        return cls._convert_decimal(raw)

    @validator("nominal_max", pre=True)
    def nominal_max_validator(  # NOQA
        cls, raw: Union[str, float, None]
    ) -> Optional[Decimal]:
        """Ensure the proper conversion of the the
        Decimal value
        """
        return cls._convert_decimal(raw)

    @staticmethod
    def _convert_decimal(raw: Union[str, float, None]) -> Optional[Decimal]:
        """Handle the decimal conversion

        Args:
            raw (Union[str, float, None]): Raw value

        Raises:
            ValueError: raised when the data type
                does not match the understood types

        Returns:
            Optional[Decimal]: None if the raw value
                corresponds to -Infinity, +Infinity or
                NaN. Decimal('0') if Decimal('-0') or
                the true value
        """

        # ensure we are working with
        # the correct type
        if isinstance(raw, str) or isinstance(raw, float) or isinstance(raw, int):
            decimal = Decimal(raw)

        # accept decimal
        elif isinstance(raw, Decimal):
            decimal = raw

        # allow None values
        elif raw is None:
            return None

        # reject the rest
        else:
            data_type = type(raw)
            raise ValueError(f"Unsupported datatype '{data_type}'")

        # interpret the values
        # handle the special values
        if decimal in {Decimal("Infinity"), Decimal("-Infinity"), Decimal("NaN")}:
            return None

        # enforce zero to be positive
        if decimal == Decimal("-0"):
            return Decimal("0")

        # accept the value
        return decimal


class W24ToleranceClass(BaseModel):
    """Tolerance Class which matches an individual attribute
    of the General Tolerances to a tolerance property and
    tolerance table

    Attributes:
        blurb: Tolerance class label for human consumption

        raw_ocr_blurb: Tolerance note text as annotated on 
            the drawing.

        property: Property that is being tolerated

        table: Rows of the tolerance table that correspond
            to the selected tolerance class
    """

    blurb: str
    raw_ocr_blurb: str
    property: W24ToleranceProperty
    table: List[W24ToleranceTableItem]


class W24GeneralTolerances(W24BaseFeatureModel):
    """
    General Tolerances on the Title Block of the Technical Drawing.

    Attributes:
        blurb: Blurb of the general tolerances for human consumption.
        tolerance_standard: General Tolerance Standard that was defined
            in the Drawing
        principle: Principle that is annotated on the general tolerance
            by "-E" (or the lack of if).
        angular_class: Angular toleration class
        flatness_class: Flatness toleration class
        straightness_class: Straightness toleration class
        linear_class: Linear toleration class
        radius_class: Radius and chamfer toleration class
        symmetry_class: Symmetry toleration class
        perpendicularity_class: Perpendicularity toleration class

    """

    blurb: str
    tolerance_standard: W24GeneralTolerancesStandard
    principle: Optional[W24GeneralTolerancesPrinciple] = None
    angular_class: Optional[W24ToleranceClass] = None
    flatness_class: Optional[W24ToleranceClass] = None
    straightness_class: Optional[W24ToleranceClass] = None
    linear_class: Optional[W24ToleranceClass] = None
    radius_class: Optional[W24ToleranceClass] = None
    runout_class: Optional[W24ToleranceClass] = None
    symmetry_class: Optional[W24ToleranceClass] = None
    perpendicularity_class: Optional[W24ToleranceClass] = None
