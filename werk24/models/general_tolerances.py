from decimal import Decimal
from enum import Enum
from typing import List, Optional, Union

from pydantic import UUID4, BaseModel, validator


class W24GeneralTolerancesStandard(str, Enum):
    """ Enum of all supported
    General Tolerance Standards
    """
    DIN_7168 = "DIN 7168"
    ISO_2768 = "ISO 2768"


class W24ToleranceProperty(str, Enum):
    """ Enum of all attributes that can
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
    """ Enum of the supported General Tolerance
    Principles.
    """
    INDEPENDENCE = "INDEPENDENCE"
    ENVELOPE = "ENVELOPE"


class W24ToleranceTableItem(BaseModel):

    @validator('nominal_min', pre=True)
    def nominal_min_validator(  # NOQA
        cls,
        raw: Union[str, float, None]
    ) -> Optional[Decimal]:
        """ Ensure the proper conversion of the the
        Decimal value
        """
        return cls._conv_decimal(raw)

    @validator('nominal_max', pre=True)
    def nominal_max_validator(  # NOQA
        cls,
        raw: Union[str, float, None]
    ) -> Optional[Decimal]:
        """ Ensure the proper conversion of the the
        Decimal value
        """
        return cls._conv_decimal(raw)

    @staticmethod
    def _conv_decimal(
        raw: Union[str, float, None]
    ) -> Optional[Decimal]:
        """ Handle the decimal converstion

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
        if isinstance(raw, str) \
            or isinstance(raw, float)\
                or isinstance(raw, int):
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
        if decimal in {
                Decimal("Infinity"),
                Decimal("-Infinity"),
                Decimal("NaN")}:
            return None

        # enforce zero to be positive
        if decimal == Decimal('-0'):
            return Decimal('0')

        # accept the value
        return decimal

    nominal_min: Optional[Decimal]
    nominal_max: Optional[Decimal]
    deviation_min: Optional[Decimal]
    deviation_max: Optional[Decimal]


class W24ToleranceClass(BaseModel):
    """ Tolerance Class which matches an individual attribute
    of the General Tolerances to a tolerance property and
    tolerance table

    Attributes:
        blurb: Tolerance class label for human consumption

        property: Property that is being tolerated

        table: Rows of the tolerance table that correspond
            to the selected tolerance class
    """
    blurb: str

    property: W24ToleranceProperty

    table: List[W24ToleranceTableItem]


class W24GeneralTolerances(BaseModel):
    """ Object representing the General Tolerances indicated
    on the Title Block of the Technical Drawing.
    """

    blurb: str
    """ Blurb of the general tolerances for human consumption
    """

    tolerance_standard: W24GeneralTolerancesStandard
    """ GeneralTolerance Standard that was defined
    in the Drawing
    """

    principle: W24GeneralTolerancesPrinciple
    """ Principle that is annotated on the general
    tolerance by "-E" (or the lack of if)
    """

    angular_class: Optional[W24ToleranceClass]
    """ Angular toleration class """

    flatness_class: Optional[W24ToleranceClass]
    """ Flatness toleration class """

    straightness_class: Optional[W24ToleranceClass]
    """ Straightness toleration class """

    linear_class: Optional[W24ToleranceClass]
    """ Linear toleration class """

    radius_class: Optional[W24ToleranceClass]
    """ Radius and chamfer toleration class """

    runout_class: Optional[W24ToleranceClass]
    """ Runout toleration class """

    symmetry_class: Optional[W24ToleranceClass]
    """ Symmetry toleration class """

    perpendicularity_class: Optional[W24ToleranceClass]
    """ Perpendicularity toleration class - not defined in DIN7168 """
