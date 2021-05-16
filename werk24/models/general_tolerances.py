from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


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
    nominal_min: float
    nominal_max: float
    deviation_min: float
    deviation_max: float


class W24ToleranceClass(BaseModel):
    """ Tolerance Class which matches an individual attribute
    of the General Tolerances to a tolerance property and
    tolerance table

    Attributes:
        blub: Tolerance class label for human consumption

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
    """ Radius andn chamfer toleration class """

    runout_class: Optional[W24ToleranceClass]
    """ Runout toleration class """

    symmetry_class: Optional[W24ToleranceClass]
    """ Symmetry toleration class """

    perpendicularity_class: Optional[W24ToleranceClass]
    """ Perpendicularity toleration class - not defined in DIN7168 """
