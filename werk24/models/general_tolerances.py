from enum import Enum
from typing import List

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


class W24ToleranceNominalRange(BaseModel):
    """ Nominal range
    """
    nominal_min: float
    nominal_max: float


class W24ToleranceDeviatons(BaseModel):
    """ Permissable deviations
    """
    deviation_min: float
    deviation_max: float


class W24ToleranceClass(BaseModel):

    blurb: str
    """ Tolerance class label for human consumption
    """

    property: W24ToleranceProperty
    """ Tolerated property
    """

    table = List[W24ToleranceNominalRange, W24ToleranceDeviatons]
    """ Toleranace matching the nomial range
    to the allowable deviations
    """


class W24ToleranceClassAngular(W24ToleranceClass):
    """ Tolerance Class for Angles
    """
    property = W24ToleranceProperty.ANGULAR


class W24ToleranceClassFlatness(W24ToleranceClass):
    """ Tolerance Class for GD&T Flattness
    """
    property = W24ToleranceProperty.FLATNESS


class W24ToleranceClassLinear(W24ToleranceClass):
    """ Tolerance Class for Linear distances
    """
    property = W24ToleranceProperty.LINEAR


class W24ToleranceClassPerpendicularity(W24ToleranceClass):
    """ Tolerance Class for GD&T Perpendicularity
    """
    property = W24ToleranceProperty.PERPENDICULARITY


class W24ToleranceClassRadius(W24ToleranceClass):
    """ Tolerance Class for Radii
    """
    property = W24ToleranceProperty.RADIUS


class W24ToleranceClassRunout(W24ToleranceClass):
    """ Tolerance Class for GD&T Runout
    """
    property = W24ToleranceProperty.RUNOUT


class W24ToleranceClassStraightness(W24ToleranceClass):
    """ Tolerance Class for GD&T Straightness
    """
    property = W24ToleranceProperty.STRAIGHTNESS


class W24ToleranceClassSymmetry(W24ToleranceClass):
    """ Tolerance Class for GD&T Symmetry
    """
    property = W24ToleranceProperty.SYMMETRY


class W24GeneralTolerances(BaseModel):

    tolerance_standard: W24GeneralTolerancesStandard

    angular_class: W24ToleranceClassAngular
    flatness_class: W24ToleranceClassFlatness
    linear_class: W24ToleranceClassLinear
    perpendicularity_class: W24ToleranceClassPerpendicularity
    radius_class: W24ToleranceClassRadius
    runout_class: W24ToleranceClassRunout
    straightness_class: W24ToleranceClassStraightness
    symmetry_class: W24ToleranceClassSymmetry


