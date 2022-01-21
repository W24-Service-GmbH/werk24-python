from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import UUID4, BaseModel

from .feature import W24Feature
from .unit import W24UnitSystem


class W24RoughnessStandard(str, Enum):
    """ Most standards that define the surface roughness use
    very similar symbols. However, the position of the fields
    varies.

    The standards listed here are understood and supported
    by the API.

    NOTE: the ISO 1302 standard exists in four different versions,
    these releases substantially modified the position and
    structure of the roughness symbols.

    NOTE: this list is not exhaustive, many countries have specified
    their own standards over the years. Do not hesitate to reach
    out if you wish us to implement another standard.

    """
    ISO_1302_1978 = "ISO 1302:1978"
    ISO_1302_1992 = "ISO 1302:1992"
    ISO_1302_2002 = "ISO 1302:2002"
    ISO_21920_1_2021 = "ISO 21920-1:2021"
    ASME_Y14_36M = "ASME Y14.36M"


class W24RoughnessMaterialRemovalType(str, Enum):
    """ Most standard allow the designer to specify
    whether material removal is required or prohibited.

    By default both options are allowed.
    """
    UNSPECIFIED = "UNSPECIFIED"
    PROHIBITED = "PROHIBITED"
    REQUIRED = "REQUIRED"


class W24RoughnessDirectionOfLay(str, Enum):
    """ The lay of the roughness limits the
    manufacturing process and is sometimes
    required for the application.
    """
    PARALLEL = "="
    PERPENDICULAR = "⟂"
    CROSS = "X"
    MULTIDIRECTIONAL = "M"
    CIRCULAR = "C"
    RADIAL = "R"
    PROTUBERANT = "P"


class W24RoughnessAcceptanceCriterion(str, Enum):
    """ The designer can specify whether to apply
    the 16%-rule, the maximum- or medium- rule
    when deciding whether a surface complies with
    the specifications.
    """
    SIXTEEN_PERCENT = "16%"
    MAXIMUM = "max"
    MEAN = "mean"


class W24RoughnessSide(str, Enum):
    """ Roughnesses can specify both, the
    upper and the lower limit (i.e., a minimum
    roughness can be required).
    """
    UPPER = "U"
    LOWER = "L"


class W24RoughnessFilterType(str, Enum):
    """ When measuring the roughness, different
    filter types will result in different results.
    To reduce this source of ambiguity, the
    designer can specify the filter to be used.

    NOTE: this list is not exhaustive. If you
    need us to support another filter method,
    please reach out.
    """
    GAUSSIAN = "G"
    ROBUST_GAUSSIAN = "RG"
    SPLINE = "S"
    TWO_RC = "\"2RC\""


class W24RoughnessProfile(str, Enum):
    """ The measured roughness (R) can be
    modified by applying high/low-pass filters
    and obtain the waviness and profile
    of a surface
    """
    ROUGHNESS = "R"
    WAVINESS = "W"
    PROFILE = "P"


class W24RoughnessCharacteristic(str, Enum):
    """ The Roughness / Waviness / Profile is
    a 2 dimensional chart (height over position).

    To obtain a single number, different methods
    can be applied. The characteristic specifies
    which one it to be used.
    """
    MAXIMUM_MEAN_TO_PEAK = "p"
    MAXIMUM_MEAN_TO_VALLEY = "v"
    MAXIMUM_PEAK_TO_VALLEY = "z"
    MEAN_HEIGHT_OF_PROFILE = "c"
    DEEPEST_VALLEY_TO_HEIGHEST_PEAK = "t"
    AVERAGE_ROUGHNESS = "a"
    ROOM_MEAN_SQUARE = "q"
    SKEWNESS = "sk"
    KURTOSIS = "ku"


class W24RoughnessGradeWarning(str, Enum):
    """ Warnings associated with the Roughness Grade.
    """

    SIZE_LARGER_THAN_NORM = "SIZE_LARGER_THAN_NORM"
    TOLERANCE_WIDTH_SMALLER_THAN_NORM = "TOLERANCE_WIDTH_SMALLER_THAN_NORM"
    TOLERANCE_WIDTH_LARGER_THAN_NORM = "TOLERANCE_WIDTH_LARGER_THAN_NORM"


class W24RoughnessGrade(BaseModel):
    """ ISO Roughness Grade

    Attributes:
        blurb: String representation for human consumption

        grade: Roughness Grade in the range N1 to N12.

        warning: The norm is limited to certain Ra/Rz ranges.
            When the tolerance falls outside that range, we
            append a warning.
    """
    blurb: str

    grade: int

    warning: Optional[W24RoughnessGradeWarning]


class W24RoughnessParameter(BaseModel):
    """ Roughness Label

    Attributes:
        blurb: String representation of the Roughness for human
            consumption.

        side: Roughness Side that is specified (upper or lower).
            We automatically determine this value depending on
            the standard and the position of the parameter

        filter_type: Filter Type to use when measuring the surface.
            When not specified on the drawing, we set the default
            value according to the applicable standard.

        micro_lambda: Filter bandwidth microroughness cutoff lambda_s.
            When not specified, we determine the default value based
            on the standard and the value_limit.

        main_lambda: Filter bandwidth main cutoff lambda_c.
            When not specified, we determine the default value based
            on the standard and the value_limit.

        profile: Profile to be measured (Profile, Roughness, Waviness)


        characteristic: Method of converting the 2D-measurement into
            a single number

        sampling_length_multiple: For sophisticated applications, the
            sample needs to be taken over a longer distance. This
            attribute specifies by how much to increase the length.
            When not specified, this will be 1.

        acceptance_criterion: Designers can specify what rule to
            apply when deciding whether a measured tolerance complies
            with the requirements

        value_limit: Specification limit

        roughness_grade: ISO roughness grade that the roughness specifications
            correspond to. IMPORTANT: this allows you to deal with
            all the standards in a simple way.

    """
    blurb: str

    side: Optional[W24RoughnessSide]

    filter_type: Optional[W24RoughnessFilterType]

    micro_lambda: Optional[Decimal]

    main_lambda: Optional[Decimal]

    profile: Optional[W24RoughnessProfile]

    characteristic: Optional[W24RoughnessCharacteristic]

    sampling_length_multiple: Optional[int]

    acceptance_criterion: Optional[W24RoughnessAcceptanceCriterion]

    value_limit: Optional[Decimal]

    roughness_grade: W24RoughnessGrade


class W24ManufacturingMethod(BaseModel):
    """ Manufacturing method specified on the drawing.
    Currently only the blurb is available.

    Attributes:
        blurb: Manufacturing method as specified on the
            drawing
    """
    blurb: str


class W24RoughnessLabel(BaseModel):
    """ Roughness Label

    blurb: String for human consumption

    blurb_html: HTML for human consumption. The complex structure of the
        symbol makes this necessary.

    standard : Standard in which the Roughness Symbol is written
        NOTE: there are multiple standards that are still in use

    machining_allowance: Machining Allowance in millimeter of micro-inch.
        See the `unit` attribute.

    material_removal_type: The MaterialRemovalType specifies whether material
        must / must not be removed.

    direction_of_lay: The lay of the roughness limits the manufacturing
        process and is sometimes required for the application.

    manufacturing_method: Method by which to achieve the roughness

    roughness_parameter_upper: Upper roughness parameter

    roughness_parameter_lower: Lower roughness parameter.
        NOTE: bother the upper and the lower specifications are
        optional. Only one of them has to be set.

    unit: Unit of the machining_allowance and the parameters


    """
    blurb: str

    blurb_html: str

    standard: W24RoughnessStandard

    machining_allowance: Optional[Decimal]

    material_removal_type: W24RoughnessMaterialRemovalType

    direction_of_lay: Optional[W24RoughnessDirectionOfLay]

    manufacturing_method: W24ManufacturingMethod

    roughness_parameter_upper: Optional[W24RoughnessParameter]

    roughness_paramater_lower: Optional[W24RoughnessParameter]

    unit_system: W24UnitSystem


class W24Roughness(W24Feature):
    """ Roughness object

    Attributes:
        roughness_id: Unique UUID4 identifier

        label: RoughnessLabel
    """
    roughness_id: UUID4

    label: W24RoughnessLabel
