from decimal import Decimal
from enum import Enum
from typing import List, Optional

from pydantic import UUID4, BaseModel

from .base_feature import W24BaseFeatureModel
from .unit import W24UnitLength, W24UnitSystem


class W24RoughnessStandard(str, Enum):
    """Most standards that define the surface roughness use
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

    NOTE: REFERENCE is a special value that is used when the
    drawing specified a reference roughness. For example: w√.

    """

    ISO_1302_1978 = "ISO 1302:1978"
    ISO_1302_1992 = "ISO 1302:1992"
    ISO_1302_2002 = "ISO 1302:2002"
    ISO_21920_1_2021 = "ISO 21920-1:2021"
    ASME_Y14_36_1978 = "ASME Y14.36-1978"
    ASME_Y14_36M_1996 = "ASME Y14.36M-1996"
    ASME_Y14_36_2018 = "ASME Y14.36-2018"
    REFERENCE = "REFERENCE"


class W24RoughnessMaterialRemovalType(str, Enum):
    """Most standard allow the designer to specify
    whether material removal is required or prohibited.

    By default both options are allowed.
    """

    UNSPECIFIED = "UNSPECIFIED"
    PROHIBITED = "PROHIBITED"
    REQUIRED = "REQUIRED"


class W24RoughnessDirectionOfLay(str, Enum):
    """The lay of the roughness limits the
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
    """The designer can specify whether to apply
    the 16%-rule, the maximum- or medium- rule
    when deciding whether a surface complies with
    the specifications.
    """

    SIXTEEN_PERCENT = "16%"
    MAXIMUM = "max"
    MEAN = "mean"


class W24RoughnessConditionType(str, Enum):
    """Roughnesses can specify, the
    upper limit, the lower limit and the
    average.
    """

    UPPER = "U"
    LOWER = "L"
    AVERAGE = "A"


class W24RoughnessFilterType(str, Enum):
    """When measuring the roughness, different
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
    TWO_RC = '"2RC"'


class W24RoughnessGrade(BaseModel):
    """ISO Roughness Grade

    Attributes:
        blurb: String representation for human consumption

        grade: Roughness Grade in the range N01 to N12.
            Valid values are N01, N0, N1, N2, N3, N4, N5,
            N6, N7, N8, N9, N10, N11, N12, N13, N14

    """

    blurb: str

    grade: str


class W24RoughnessParameter(str, Enum):
    """Roughness Parameter that is specified.

    NOTE: this list is not exhaustive, but
    covers the most frequently used parameters.
    """

    # ASME
    AA = "AA"
    CLA = "CLA"
    PVA = "PVA"
    RMS = "RMS"

    # PROFILE
    PA = "Pa"
    PC = "PC"
    PKU = "Pku"
    PP = "Pp"
    PQ = "Pq"
    PSK = "Psk"
    PT = "Pt"
    PV = "Pv"
    PY = "Py"
    PZ = "Pz"

    # ROUGHNESS
    RA_DIN = "Ra(DIN)"
    RA_ISO = "Ra(ISO)"
    RC = "Rc"
    RKU = "Rku"
    RP = "Rp"
    RQ = "Rq"
    RSK = "Rsk"
    RT = "Rt"
    RV = "Rv"
    RY = "Ry"
    RZ = "Rz"

    # WAVINESS
    WA = "Wa"
    WC = "Wc"
    WKU = "Wku"
    WP = "Wp"
    WQ = "Wq"
    WSK = "Wsk"
    WT = "Wt"
    WV = "Wv"
    WY = "Wy"
    WZ = "Wz"

    # N-GRADE
    N = "N"


class W24RoughnessEvaluationLengthType(str, Enum):
    LENGTH = "LENGTH"
    LAMBDA_C_MULTIPLE = "LAMBDA_C_MULTIPLE"


class W24RoughnessEvaluationLength(BaseModel):
    """For sophisticated application, the sample needs
    to be taken over a longer distances. This is specified the
    either the sampling length in millimeter (ISO 3012:1974,
    ISO 3012:1978, ISO 3012:1992) or as multiple of the main lambda
    (ISO 3012:2002 and ISO 3012:2021).


    Attributes:
        evaluation_length_type: Sampling length type that is specified
            by the applicable standard

        length: evaluation length in the specified units.

        length_unit: Millimeter for both the ISO and ASME standards

        lambda_c_multiple: multiple of the main cutoff lambda_c

    """

    evaluation_length_type: W24RoughnessEvaluationLengthType

    length: Optional[Decimal]
    length_unit: Optional[W24UnitLength]

    lambda_c_multiple: Optional[Decimal]


class W24RoughnessCondition(BaseModel):
    """Roughness Label

    Attributes:
        blurb: String representation of the Roughness for human
            consumption.

        condition_type: Roughness Side that is specified (upper or lower).
            We automatically determine this value depending on
            the standard and the position of the parameter

        filter_type: Filter Type to use when measuring the surface.
            When not specified on the drawing, we set the default
            value according to the applicable standard.

        lambda_s: Filter bandwidth microroughness cutoff lambda_s.
            When not specified, we determine the default value based
            on the standard and the value_limit.

        lambda_c: Filter bandwidth main cutoff lambda_c.
            When not specified, we determine the default value based
            on the standard and the value_limit.

        parameter: Parameter to be measured


        characteristic: Method of converting the 2D-measurement into
            a single number

        evaluation_length: For sophisticated application, the roughness needs
            to be evaluated over a longer distances. This is specified the
            either the sampling length in millimeter (ISO 3012:1974,
            ISO 3012:1978, ISO 3012:1992) or as multiple of the main lambda
            (ISO 3012:2002 and ISO 3012:2021).

        acceptance_criterion: Designers can specify what rule to
            apply when deciding whether a measured tolerance complies
            with the requirements

        value_limit: Specification limit

        roughness_grade: ISO roughness grade that the roughness specifications
            correspond to. IMPORTANT: this allows you to deal with
            all the standards in a simple way.

    """

    blurb: str

    condition_type: Optional[W24RoughnessConditionType]

    filter_type: Optional[W24RoughnessFilterType]

    lambda_s: Optional[Decimal]

    lambda_c: Optional[Decimal]

    parameter: Optional[W24RoughnessParameter]

    evaluation_length: Optional[W24RoughnessEvaluationLength]

    acceptance_criterion: Optional[W24RoughnessAcceptanceCriterion]

    value: Optional[Decimal]

    roughness_grade: Optional[W24RoughnessGrade]


class W24ManufacturingMethod(BaseModel):
    """Manufacturing method specified on the drawing.
    Currently only the blurb is available.

    Attributes:
        blurb: Manufacturing method as specified on the
            drawing
    """

    blurb: str


class W24RoughnessWaviness(BaseModel):
    """Roughness Waviness as defined in the ASME-Y14-36

    Attributes:
        waviness_height: Waviness height in inch
        waviness_width: Waviness width in inch
    """

    waviness_height: Decimal
    waviness_width: Decimal


class W24RoughnessLabel(BaseModel):
    """Roughness Label

    Attributes:
        blurb: String for human consumption

        blurb_html: HTML for human consumption. The complex structure of the
            symbol makes this necessary.

        standard : Standard in which the Roughness Symbol is written
            NOTE: there are multiple standards that are in use

        machining_allowance: Machining Allowance in millimeter of micro-inch.
            See the `unit` attribute.

        material_removal_type: The MaterialRemovalType specifies whether material
            must / must not be removed.

        applies_all_around: Boolean value that specifies whether the roughness
            applies to all surfaces around

        direction_of_lay: The lay of the roughness limits the manufacturing
            process and is sometimes required for the application.

        manufacturing_method: Method by which to achieve the roughness

        conditions: Roughness conditions

        unit_system: Unit system that is used for the roughness.
            We are not using the explicit units as the different
            attributes have different units (e.g, micro and nano meters)

        waviness: Waviness defined in ASME standards

        variable: Roughness variable that is used in roughness references.

    """

    blurb: str

    blurb_html: str

    standard: W24RoughnessStandard

    machining_allowance: Optional[Decimal]

    material_removal_type: W24RoughnessMaterialRemovalType

    applies_all_around: bool

    direction_of_lay: Optional[W24RoughnessDirectionOfLay]

    manufacturing_method: W24ManufacturingMethod

    conditions: List[W24RoughnessCondition]

    unit_system: W24UnitSystem

    waviness: Optional[W24RoughnessWaviness]

    variable: Optional[str] = None


class W24Roughness(W24BaseFeatureModel):
    """Roughness object

    Attributes:
        roughness_id: Unique UUID4 identifier

        label: RoughnessLabel
    """

    roughness_id: UUID4
    label: W24RoughnessLabel


class W24RoughnessReference(W24BaseFeatureModel):
    """Roughness Reference

    Attributes:
    ----------
    blurb: String for human consumption

    reference_label: Placeholder for the roughness.
        We are using a reference label here to allow
        the full scope of the roughness to be specified.
        Sometimes we see a pure "material removal not
        permitted" symbol as placeholder.

    reference_value: Meaning of the roughness_label,
        explaining what surface roughness is applicable
        when the roughness_label is specified on a
        workpiece.

    """

    blurb: str
    reference_label: W24RoughnessLabel
    reference_value: W24RoughnessLabel


class W24GeneralRoughness(W24BaseFeatureModel):
    """General Roughness object

    Attributes:
    ----------
    blurb: String for human consumption

    general_roughnesses: Surface Roughness Specification
        required for all surfaces of a workpiece. Unless
        any deviation is specified.

    deviating_roughnesses: Indicates deviations from
        the general surface roughness requirements.
    """

    blurb: str
    general_roughnesses: List[W24RoughnessLabel]
    deviating_roughnesses: List[W24RoughnessLabel]
