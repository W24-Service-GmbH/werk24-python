import abc
from enum import Enum
from typing import List, Optional, Tuple

from pydantic import BaseModel, UUID4


class W24GDTCharacteristic(str, Enum):
    """ Enum of all possible Characteristics
    following ISO 1101.

    !!! note
        When the GDT frame only describes the location
        of a reference datum, the value DATUM_INDICATOR is used
    """
    FORM_STRAIGHTNESS = "⏤"
    FORM_FLATNESS = "⏥"
    FORM_CIRCULARITY = "○"
    FORM_CYLINDRICITY = "⌭"
    PROFILE_OF_SURFACE = "⌓"
    PROFILE_OF_LINE = "⌒"
    ORIENTATION_PERPENDICULARITY = "⟂"
    ORIENTATION_ANGULARITY = "∠"
    ORIENTATION_PARALLELISM = "∥"
    LOCATION_POSITION = "⌖"
    LOCATION_CONCENTRICITY = "◎"
    LOCATION_SYMMETRY = "⌯"
    RUNOUT_CIRCULAR = "↗"
    RUNOUT_TOTAL = "⌰"
    DATUM_INDICATOR = "[DATUM]"


class W24GDTFeatureAssociated(str, Enum):
    """ Enum of all associated toleranced features
    """
    MINIMAX = "Ⓒ"
    GAUSSIAN = "Ⓖ"
    MIN_CIRCUMSCRIBED = "Ⓝ"
    MAX_CIRCUMSCRIBED = "Ⓧ"
    TANGENT = "Ⓣ"


class W24GDTFeatureDerived(str, Enum):
    """ Enum of all derived features
    """
    PROJECTED = "Ⓟ"
    MEAN = "Ⓐ"


class W24GDTZoneCombination(str, Enum):
    """ Enum of all tolerance zonce combinations
    """
    COMBINED = "CZ"
    SEPARATED = "SZ"


class W24GDTZoneShape(str, Enum):
    """ Enum of all zone shapes
    """
    DIAMETER = "Ø"
    DIAMETER_SPHERE = "S⌀"


class W24GDTZoneConstraint(str, Enum):
    """ Enum of the Zone Contraints
    """
    UNSPECIFIED_INCLINATION = "OZ"
    UNSPECIFIED_OFFSET = "VA"


class W24GDTDatum(BaseModel):
    """ Preliminary implementation of the GD&T Datum

    Attributes:
        blurb: Reference name. Typically: A,B,C ...
            Can also contain more complex names, e.g., (A-B-C-D)[CM]

    !!! note
        Future implementations might allow fine-grained
        access to the attributes of complex names:
        e.g., (A-B-C-D)[CM]
    """

    blurb: str


class W24GDTZoneOffset(BaseModel):
    """ Specified offset indicated by leading UZ...

    Attributes:
        blurb: blurb of the specified offset for human consumption.
            e.g., UZ+0.15, UZ-0.2, UZ+0.1:0.2
    """

    blurb: str


class W24GDTZoneValue(BaseModel):
    """ Preliminary defintion of the GDT Zone Value
    Future implementation will give access to the
    width and extend seperately

    Attributes:

        blurb: String representation for human consumption
            e.g., 0.05/12x10°

        width_min: Minimal width. Also used when no maximal width
            is defined.

        width_max: Optional maximal width.

        extend_quantity: Optional quantity of the spacing

        extend_shape: Optional shape of the extend

        extend_value: Optional extend value

        extend_angle: Optional angle of the extend
    """

    blurb: str

    width_min: float

    width_max: Optional[float]

    extend_quantity: Optional[int]

    extend_shape: Optional[W24GDTZoneShape]

    extend_value: Optional[float]

    extend_angle: Optional[float]


class W24GDTFilterType(str, Enum):
    """ Preliminary list of feature filters

    Filters remaining: RG, S, OH, SW, AB, CW
    """
    GAUSSIAN = "G"


class W24GDTFilter(BaseModel, abc.ABC):
    """ Abstract base class to describe feature filters

    Attributes:
        blurb: String representation of the file for human consumption

        filter_type: Filter Type to facilitate deserialization
    """

    blurb: str

    filter_type: W24GDTFilterType


# class W24GDTFilterG(W24GDTFilter):
#     """ Gaussian Feature filter without contraints
#     """
#     filter_type = W24GDTFilterType.GAUSSIAN

#     wavelength_min: float
#     """ Minimum wavelength in wavers/revolution
#     """

#     wavelength_max: float
#     """ Maximum wavelength in wavers/revolution
#     """


class W24GDTReferenceAssociation(str, Enum):
    """ Association of the Reference Element
    """

    MINIMAX = "C"
    """ Minimax (Tschebyschew-) Element without contraint
    """

    MINIMAX_EXTERNAL = "CE"
    """ Minimax (Tschebyschew-) Element with external
    constraint
    """

    MINIMAX_INTERNAL = "CI"
    """ Minimal (Tschebyschew-) Element with internal
    constraint
    """

    GAUSSIAN = "G"
    """ Gaussian Least Square Element without constraint
    """

    GAUSSIAN_EXTERNAL = "GE"
    """ Gaussian Least Square Element with external
    constraint
    """

    GAUSSIAN_INTERNAL = "GI"
    """ Gaussian Least Square Element with external
    constraint
    """

    MIN_CIRCUMSCRIBED = "N"
    """ Minimal circumscribed element
    """

    MAX_CIRCUMSCRIBED = "X"
    """ Maximal circumscribed element
    """


class W24GDTReferenceParameter(str, Enum):
    """ Parameter of the reference element
    """

    PEAK_VALUE = "P"
    """ Highest value
    """

    VALLEY_VALUE = "V"
    """ Lowest value
    """

    DEVISATION_SPAN = "T"
    """ Deviation span
    """

    STANDARD_DEVIATION = "Q"
    """ Root mean square deviation
    """


class W24GDTMaterialCondition(str, Enum):
    """ Enum for Material Conditions
    """

    MAXIMUM = "Ⓜ"
    """ Maximum material condition (MMC)
    """

    MINIMUM = "Ⓛ"
    """ Mimimal material condition (LMC)
    """

    RECIPROCITY = "Ⓡ"
    """ Reciprocity
    """


class W24GDTState(str, Enum):
    """ Enum for the State
    """
    FREE = "Ⓕ"


class W24GDTFrame(BaseModel):
    """ Representation of the Geometric Dimensioning
    and Toleration frame

    Attributes:
        gdt_id: Unique id of the GDT

        blurb: String representation of the label for human consumption
            e.g., [⌖|⌀0.3Ⓜ|A|B|C]

        characteristic: Section for gemetric characteristic e.g.: ⌓

        zone_shape: Tolerance zone shape, e.g, S⌀

        zone_value: GDT value: e.g., 0.03
            Is optional to supprt Datum Feature Indicators

        zone_combinations: Ordered list of zone combinations, e.g., CZ, SZ

        zone_offset: Optional specified offset, e.g., UZ-0.2

        zone_constraint: Optional zone constraint: e.g., OZ, VA

        feature_filter: Optional feature filter

        feature_associated: Associated toleraced feature

        feature_derived: Derived Feature

        reference_association: Reference element association

        reference_parameter: Reference element parameter

        material_condition: Material condition

        state: FREE or None

        data: Ordered list of data

    """
    gdt_id: Optional[UUID4] = None

    blurb: str

    characteristic: W24GDTCharacteristic

    zone_shape: Optional[W24GDTZoneShape] = None

    zone_value: Optional[W24GDTZoneValue]

    zone_combinations: List[W24GDTZoneCombination] = []

    zone_offset: Optional[W24GDTZoneOffset] = None

    zone_constraint: Optional[W24GDTZoneConstraint] = None

    feature_filter: Optional[W24GDTFilter] = None

    feature_associated: Optional[W24GDTFeatureAssociated] = None

    feature_derived: Optional[W24GDTFeatureDerived] = None

    reference_association: Optional[W24GDTReferenceAssociation] = None

    reference_parameter: Optional[W24GDTReferenceParameter] = None

    material_condition: Optional[W24GDTMaterialCondition] = None

    state: Optional[W24GDTState] = None

    data: List[W24GDTDatum] = []


class W24GDT(BaseModel):
    """ Parent object for Geometric Dimensionsing and Toleration
    Frames, attaching them to the physical location on the drawing.

    Attributes:
        bounding_polygon: Bounding polygon of the GDT annotation as
            tuple of x, y coordinates in the pixel coordinate system of
            the sectional.
            Simple GDTs are represented by a simple rectangle.
            To support more complex GDTs (e.g., with a Sectional
            Plane Indicator, we define a polygon).
            The polygon starts at the top left and is
            oriented clock-wise.

        frame: Representation of the GDT frame

    """

    bounding_polygon: List[Tuple[float, float]]

    frame: W24GDTFrame

    # measure_label: Optional[W24MeasureLabel] = None
    """ Optional size dimension, typically annotated
    above the feature control frame.

    Example:
        ⌀12.0 + /- 0.1
        [⊥|⌀0.1Ⓜ| A]
    """

    # sectional_plane
    """ Definition of Sectional Plane Indicator will
    follow.
    Example: ⟨[∥| A]
    """  # pylint: disable=pointless-string-statement

    # orientation_plane
    """ Definition of the Orientational Plane Indicator
    will follow
    Example: ⟨[∥| A]⟩
    """  # pylint: disable=pointless-string-statement

    # direction_feature
    """ Defintion of the Direction Feature Indicator
    will follow
    Example: ←[∥| A]
    """  # pylint: disable=pointless-string-statement

    # collection_plane
    """ Defintion of the Collection Plane Indicator
    will follow
    Exmple: ◯[∥| B]
    """  # pylint: disable=pointless-string-statement
