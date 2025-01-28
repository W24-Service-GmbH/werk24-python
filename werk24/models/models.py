from datetime import date
from decimal import Decimal
from fractions import Fraction
from typing import Annotated, List, Literal, Optional, Tuple

from pint import Quantity as PintQuantity
from pint import UnitRegistry
from pydantic import (
    BaseModel,
    BeforeValidator,
    ConfigDict,
    Field,
    PlainSerializer,
    WithJsonSchema,
)

from .enums import (
    CueType,
    CurvatureType,
    GDnTAssociatedFeature,
    GDnTAssociatedReference,
    GDnTCharacteristic,
    GDnTDerivedFeature,
    GDnTFilterType,
    GDnTMaterialCondition,
    GDnTReferenceParameter,
    GDnTState,
    GDnTZoneCombination,
    GDnTZoneConstraint,
    GeneralTolerancesPrinciple,
    GeneralTolerancesStandard,
    GeometryType,
    IdentifierPeriod,
    IdentifierStakeholder,
    IdentifierType,
    Language,
    MaterialCategory1,
    MaterialCategory2,
    MaterialCategory3,
    NoteType,
    RoughnessAcceptanceCriterion,
    RoughnessConditionType,
    RoughnessDirectionOfLay,
    RoughnessFilterType,
    RoughnessMaterialRemovalType,
    RoughnessParameter,
    RoughnessStandard,
    SizeType,
    ThreadHandedness,
    ThreadType,
    Unit,
)

ureg = UnitRegistry()

Quantity = Annotated[
    PintQuantity,
    BeforeValidator(lambda x: x if isinstance(x, PintQuantity) else ureg(str(x))),
    PlainSerializer(lambda x: str(x), return_type=str),
    WithJsonSchema({"type": "string"}, mode="serialization"),
    WithJsonSchema({"type": "string"}, mode="validation"),
]


class Entry(BaseModel):

    language: Optional[Language] = Field(
        None,
        description="The language of the identifier, if known.",
        examples=[Language.ENG, Language.DEU],
    )

    value: str = Field(
        ...,
        min_length=1,
        description="The value of the identifier. Must be a non-empty string.",
        examples=["12345-ABC"],
    )


class Identifier(Entry):
    """
    Represents an identifier (such as the drawing number) used for distinguishing elements in a drawing.

    Attributes:
    ----------
    - identifier_type (IdentifierType): The type of the identifier (e.g., part ID, drawing ID).
    - stakeholder (Optional[IdentifierStakeholder]): The associated stakeholder (if known).
    - period (Optional[IdentifierPeriod]): The associated period (if known).
    - value (str): The actual value of the identifier.
    """

    identifier_type: IdentifierType = Field(
        ..., description="The type of identifier, such as part ID or drawing ID."
    )

    stakeholder: Optional[IdentifierStakeholder] = Field(
        None,
        description="The associated stakeholder, if known.",
        examples=[IdentifierStakeholder.SUPPLIER, IdentifierStakeholder.OWNER],
    )

    period: Optional[IdentifierPeriod] = Field(
        None,
        description="The associated period, if known.",
        examples=[IdentifierPeriod.PREVIOUS, IdentifierPeriod.CURRENT],
    )


class GeneralTolerances(BaseModel):
    """
    Model representing general tolerances for a part or drawing.

    General tolerances are applied to dimensions where specific tolerances are not explicitly defined.
    These tolerances are governed by recognized standards and principles.

    Attributes:
    ----------
    - tolerance_standard (GeneralTolerancesStandard): The standard used to define general tolerances,
      such as DIN 7168 or ISO 2768.
    - tolerance_class (Optional[str]): The tolerance class or grade, represented by a short string (e.g., 'm', 'f', or 'c').
      This defines the degree of precision required as per the selected standard.
    - principle (GeneralTolerancesPrinciple): The principle applied to tolerance interpretation, such as independence
      (each dimension is treated independently) or envelope (dimensions must fit within an overall envelope).
    """

    tolerance_standard: GeneralTolerancesStandard = Field(
        ...,
        description="The standard used for general tolerance definitions, e.g., DIN 7168 or ISO 2768.",
        example=GeneralTolerancesStandard.ISO_2768,
    )

    tolerance_class: Optional[str] = Field(
        ...,
        description="The tolerance class or grade, defined as a short string such as 'm', 'f', or 'c'.",
        example="m",
    )

    principle: GeneralTolerancesPrinciple = Field(
        ...,
        description="The principle governing the tolerance application, such as independence or envelope.",
        example=GeneralTolerancesPrinciple.INDEPENDENCE,
    )


class Balloon(BaseModel):
    """
    Represents a balloon annotation in a drawing or part diagram.

    Attributes:
    ----------
    - label (str): The identifier displayed within the balloon.
    - center (Tuple[int, int]): The (x, y) coordinates of the balloon's center.
    - width (int): The width of the balloon in pixels.
    - height (int): The height of the balloon in pixels.
    """

    label: str = Field(
        ...,
        description="The text or identifier displayed within the balloon.",
        example="1",
    )

    center: Tuple[int, int] = Field(
        ...,
        description="The (x, y) coordinates of the balloon's center on the diagram.",
        example=(150, 200),
    )

    width: int = Field(
        ...,
        ge=1,
        description="The width of the balloon in pixels or units. Must be a positive integer.",
        example=30,
    )

    height: int = Field(
        ...,
        ge=1,
        description="The height of the balloon in pixels or units. Must be a positive integer.",
        example=30,
    )


class Cue(BaseModel):
    """
    Represents a design or manufacturing cue with descriptive information and metadata.

    Attributes:
    ----------
    - blurb (str): A short description or note associated with the cue.
    - cue_type (CueType): The type of cue, as defined in the CueType enumeration.
    - balloon (Optional[Balloon]): Optional balloon indicating the location of the cue on the drawing.
    """

    blurb: str  # Description or explanation of the cue
    cue_type: CueType  # The type of cue, constrained to values in CueType
    balloon: Optional[Balloon] = None  # Additional related information, optional


class Tolerance(BaseModel):
    """
    Represents a tolerance specification for a part or feature.

    Attributes:
    ----------
    - tolerance_grade (Optional[str]): The grade of tolerance, e.g., 'IT7' or 'H7'. Optional.
    - deviation_lower (Optional[Decimal]): The lower deviation limit. None if not specified.
    - deviation_upper (Optional[Decimal]): The upper deviation limit. None if not specified.
    - fit (Optional[str]): The type of fit, such as 'H7/h6', or None if not applicable.
    - is_theoretically_exact (bool): Indicates whether the tolerance is theoretically exact.
    - is_reference (bool): Indicates whether the tolerance serves as a reference.
    - general_tolerance_applied (bool): Indicates whether the general tolerance was applied.
    """

    tolerance_grade: Optional[str] = Field(
        None,
        description="The grade of tolerance, such as 'IT7' for an 'H7' fit. Calcuated if not specified.",
        example="IT7",
    )

    deviation_lower: Optional[Decimal] = Field(
        None,
        description="The lower deviation limit in the specified unit. Use None if unspecified.",
        example=Decimal("-0.05"),
    )

    deviation_upper: Optional[Decimal] = Field(
        None,
        description="The upper deviation limit in the specified unit. Use None if unspecified.",
        example=Decimal("0.05"),
    )

    fit: Optional[str] = Field(
        None,
        description="The fit specification, such as 'H7'. Optional if not applicable.",
        example="H7",
    )

    is_theoretically_exact: bool = Field(
        False,
        description="Whether the tolerance is theoretically exact (e.g., basic dimensions).",
        example=True,
    )

    is_reference: bool = Field(
        False,
        description="Whether the tolerance serves as a reference dimension.",
        example=False,
    )

    general_tolerance_applied: bool = Field(
        False,
        description="Whether the general tolerance was applied to this dimension.",
        example=True,
    )


class Size(BaseModel):
    """
    Represents a size definition for a part or feature in an engineering context.

    Attributes:
    ----------
    - size_type (SizeType): The type of size (e.g., diameter, linear, angular) as defined by `SizeType`.
    - nominal_size (Decimal): The nominal size value without tolerances applied.
    - tolerance (Tolerance): The tolerance specifications associated with this size.
        If no tolerance is set, the general tolerance applies.
    - unit (Unit): The unit of measurement for the size (e.g., mm, inch).
    """

    size_type: SizeType = Field(
        ...,
        description="The type of size (e.g., diameter, linear, angular).",
        example=SizeType.DIAMETER,
    )

    nominal_size: Decimal = Field(
        ...,
        ge=0,
        description="The nominal size value, which is the target dimension without tolerances.",
        example=Decimal("15.3"),
    )

    tolerance: Optional[Tolerance] = Field(
        None,
        description="The tolerance specifications associated with the size.",
        example=Tolerance(
            fit="H7",
            deviation_lower=Decimal("-0.05"),
            deviation_upper=Decimal("0.05"),
            tolerance_grade="IT7",
        ),
    )

    unit: Unit = Field(
        ...,
        description="The unit of measurement for the size (e.g., mm, inch).",
        example=Unit.MILLIMETER,
    )


class Dimension(Cue):
    """
    Represents a measurement cue in an engineering or technical drawing.

    Attributes:
    ----------
    - callout_type (Literal[CueType.MEASURE]): The type of cue, fixed to "MEASURE" for this class.
    - quantity (Decimal): The quantity or value associated with the measurement (e.g., length, diameter).
    - size (Size): The size details including size type, nominal size, tolerance, and unit.
    """

    callout_type: Literal[CueType.DIMENSION] = CueType.DIMENSION
    """ The type of cue, always set to 'MEASURE' for measurement cues. """

    quantity: int = Field(
        ...,
        ge=0,
        description="The quantity or value associated with the measurement, must be non-negative.",
        example=10,
    )

    size: Size = Field(
        ...,
        description="Details about the size, including type, nominal value, tolerance, and unit.",
    )


class Thread(Cue):
    """
    Represents a generic threaded feature in an engineering or technical drawing.

    Attributes:
    ----------
    - quantity (Decimal): The number of threads or instances.
    - diameter (Size): The diameter of the thread, including nominal size and tolerances.
    - pitch (Size): The pitch of the thread, defining the distance between thread crests.
    - threads_per_inch (Decimal): The number of threads per inch for imperial threads.
    - handedness (ThreadHandedness): The direction of the thread (e.g., LEFT or RIGHT).
    - length (Size): The length of the threaded feature.
    """

    cue_type: Literal[CueType.THREAD] = CueType.THREAD
    quantity: Decimal = Field(
        ...,
        ge=0,
        description="The number of threads or instances. Must be non-negative.",
        example=Decimal("1"),
    )

    diameter: Size = Field(
        ...,
        description="The diameter of the thread, including nominal size and tolerances.",
    )

    pitch: Size = Field(
        ...,
        description="The pitch of the thread, defining the distance between thread crests.",
    )

    threads_per_inch: Decimal = Field(
        ...,
        ge=0,
        description="The number of threads per inch (TPI) for imperial threads. Must be non-negative.",
        example=Decimal("20"),
    )

    handedness: ThreadHandedness = Field(
        ..., description="The direction of the thread, such as LEFT or RIGHT."
    )

    length: Size = Field(
        ...,
        description="The length of the threaded feature, including nominal size and tolerances.",
    )


class ThreadISOMetric(Thread):
    """
    Represents an ISO Metric thread.

    Attributes:
    ----------
    - thread_type (Literal[ThreadType.ISO_METRIC]): Specifies the thread type as ISO Metric.
    - female_major_diameter_tolerance (Tolerance): Tolerance for the major diameter of female threads.
    - female_pitch_diameter_tolerance (Tolerance): Tolerance for the pitch diameter of female threads.
    - male_major_diameter_tolerance (Tolerance): Tolerance for the major diameter of male threads.
    - male_pitch_diameter_tolerance (Tolerance): Tolerance for the pitch diameter of male threads.
    """

    thread_type: Literal[ThreadType.ISO_METRIC] = ThreadType.ISO_METRIC
    female_major_diameter_tolerance: Tolerance
    female_pitch_diameter_tolerance: Tolerance
    male_major_diameter_tolerance: Tolerance
    male_pitch_diameter_tolerance: Tolerance


class ThreadSM(Thread):
    """
    Represents a screw machine (SM) thread.

    Attributes:
    ----------
    - thread_type (Literal[ThreadType.SM]): Specifies the thread type as SM.
    - sm_size (Decimal): The size of the SM thread.
    """

    thread_type: Literal[ThreadType.SM] = ThreadType.SM
    sm_size: Decimal


class ThreadUTS(Thread):
    """
    Represents a Unified Thread Standard (UTS) thread.

    Attributes:
    ----------
    - thread_type (Literal[ThreadType.UTS]): Specifies the thread type as UTS.
    - uts_size (str): The size designation of the UTS thread (e.g., '1/4', '1/2').
    - uts_series (str): The series designation of the UTS thread (e.g., 'UNC', 'UNF').
    - tolerance_class (str): The tolerance class for the UTS thread (e.g., '2A', '3B').
    """

    thread_type: Literal[ThreadType.UTS] = ThreadType.UTS
    uts_size: str
    uts_series: str
    tolerance_class: str


class ThreadACME(Thread):
    """
    Represents an ACME thread.

    Attributes:
    ----------
    - thread_type (Literal[ThreadType.ACME]): Specifies the thread type as ACME.
    - acme_size (Decimal): The nominal size of the ACME thread.
    - acme_series (str): The series designation of the ACME thread.
    """

    thread_type: Literal[ThreadType.ACME] = ThreadType.ACME
    acme_size: Decimal
    acme_series: str


class ThreadWhitworth(Thread):
    """
    Represents a Whitworth thread.

    Attributes:
    ----------
    - thread_type (Literal[ThreadType.WHITWORTH]): Specifies the thread type as Whitworth.
    - whitworth_size (Decimal): The nominal size of the Whitworth thread.
    - whitworth_tolerance_class (Optional[str]): The tolerance class for the Whitworth thread.
    """

    thread_type: Literal[ThreadType.WHITWORTH] = ThreadType.WHITWORTH
    whitworth_size: Decimal
    whitworth_tolerance_class: Optional[str]


class ThreadKnuckle(Thread):
    """
    Represents a Knuckle thread.

    Attributes:
    ----------
    - thread_type (Literal[ThreadType.KNUCKLE]): Specifies the thread type as Knuckle.
    - knuckle_size (Decimal): The nominal size of the Knuckle thread.
    - knuckle_series (str): The series designation of the Knuckle thread.
    - knuckle_profile (Optional[Fraction]): The profile of the Knuckle thread, represented as a fraction.
    """

    thread_type: Literal[ThreadType.KNUCKLE] = ThreadType.KNUCKLE
    knuckle_size: Decimal
    knuckle_series: str
    knuckle_profile: Fraction


class Chamfer(Cue):
    """
    Represents a chamfer feature in an engineering or technical drawing.

    Attributes:
    ----------
    - cue_type (Literal[CueType.CHAMFER]): The type of cue, fixed to "CHAMFER" for this class.
    - size (Size): The linear size of the chamfer (e.g., the width or depth of the chamfer).
    - angle (Size): The angle of the chamfer, typically in degrees (e.g., 45°).
    """

    cue_type: Literal[CueType.CHAMFER] = CueType.CHAMFER
    size: Size = Field(
        ...,
        description="The linear size of the chamfer, such as the width or depth.",
        example=Size(
            size_type=SizeType.LINEAR,
            nominal_size=Decimal("2"),
            tolerance=Tolerance(
                tolerance_grade="IT7",
                deviation_lower=Decimal("-0.1"),
                deviation_upper=Decimal("0.1"),
                fit=None,
                is_theoretically_exact=False,
                is_reference=False,
            ),
            unit=Unit.MILLIMETER,
        ),
    )
    angle: Size = Field(
        ...,
        description="The angle of the chamfer, typically specified in degrees.",
        example=Size(
            size_type=SizeType.ANGULAR,
            nominal_size=Decimal("45"),
            tolerance=Tolerance(
                tolerance_grade="IT8",
                deviation_lower=Decimal("-0.5"),
                deviation_upper=Decimal("0.5"),
                fit=None,
                is_theoretically_exact=False,
                is_reference=False,
            ),
            unit=Unit.DEGREE,
        ),
    )


class Counterbore(BaseModel):
    """
    Represents a counterbore feature in an engineering or technical drawing.

    Attributes:
    ----------
    - diameter (Size): The diameter of the counterbore.
    - depth (Size): The depth of the counterbore.
    """

    diameter: Size = Field(
        ...,
        description="The diameter of the counterbore.",
        example=Size(
            size_type=SizeType.DIAMETER,
            nominal_size=Decimal("10"),
            tolerance=Tolerance(
                tolerance_grade="IT7",
                deviation_lower=Decimal("-0.1"),
                deviation_upper=Decimal("0.1"),
                fit=None,
                is_theoretically_exact=False,
                is_reference=False,
            ),
            unit=Unit.MILLIMETER,
        ),
    )
    depth: Size = Field(
        ...,
        description="The depth of the counterbore.",
        example=Size(
            size_type=SizeType.LINEAR,
            nominal_size=Decimal("5"),
            tolerance=Tolerance(
                tolerance_grade="IT8",
                deviation_lower=Decimal("-0.2"),
                deviation_upper=Decimal("0.2"),
                fit=None,
                is_theoretically_exact=False,
                is_reference=False,
            ),
            unit=Unit.MILLIMETER,
        ),
    )


class Countersink(BaseModel):
    """
    Represents a countersink feature in an engineering or technical drawing.

    Attributes:
    ----------
    - diameter (Size): The diameter of the countersink.
    - angle (Size): The angle of the countersink.
    """

    diameter: Size = Field(
        ...,
        description="The diameter of the countersink.",
        example=Size(
            size_type=SizeType.DIAMETER,
            nominal_size=Decimal("15"),
            tolerance=None,
            unit=Unit.MILLIMETER,
        ),
    )
    angle: Size = Field(
        ...,
        description="The angle of the countersink, typically in degrees.",
        example=Size(
            size_type=SizeType.ANGULAR,
            nominal_size=Decimal("90"),
            tolerance=None,
            unit=Unit.DEGREE,
        ),
    )


class Counterdrill(BaseModel):
    """
    Represents a counterdrill feature in an engineering or technical drawing.

    Attributes:
    ----------
    - diameter (Size): The diameter of the counterdrill.
    - depth (Size): The depth of the counterdrill.
    - angle (Size): The angle of the counterdrill.
    """

    diameter: Size = Field(
        ...,
        description="The diameter of the counterdrill.",
        example=Size(
            size_type=SizeType.DIAMETER,
            nominal_size=Decimal("8"),
            tolerance=None,
            unit=Unit.MILLIMETER,
        ),
    )
    depth: Size = Field(
        ...,
        description="The depth of the counterdrill.",
        example=Size(
            size_type=SizeType.LINEAR,
            nominal_size=Decimal("20"),
            tolerance=None,
            unit=Unit.MILLIMETER,
        ),
    )
    angle: Size = Field(
        ...,
        description="The angle of the counterdrill, typically in degrees.",
        example=Size(
            size_type=SizeType.ANGULAR,
            nominal_size=Decimal("118"),
            tolerance=None,
            unit=Unit.DEGREE,
        ),
    )


class Bore(BaseModel):
    """
    Represents a bore feature in an engineering or technical drawing.

    Attributes:
    ----------
    - cue_type (Literal[CueType.BORE]): The type of cue, fixed to "BORE" for this class.
    - quantity (Decimal): The number of bores or instances.
    - counterbore (Optional[Counterbore]): The counterbore feature, if present.
    - countersink (Optional[Countersink]): The countersink feature, if present.
    - counterdrill (Optional[Counterdrill]): The counterdrill feature, if present.
    - diameter (Size): The diameter of the bore.
    - depth (Size): The depth of the bore.
    - thread (Optional[Thread]): The threaded feature within the bore, if applicable.
    """

    cue_type: Literal[CueType.BORE] = CueType.BORE
    quantity: Decimal = Field(
        ...,
        ge=1,
        description="The number of bores or instances. Must be at least 1.",
        example=Decimal("2"),
    )
    counterbore: Optional[Counterbore] = Field(
        None, description="The counterbore feature, if present."
    )
    countersink: Optional[Countersink] = Field(
        None, description="The countersink feature, if present."
    )
    counterdrill: Optional[Counterdrill] = Field(
        None, description="The counterdrill feature, if present."
    )
    diameter: Size = Field(
        ...,
        description="The diameter of the bore.",
        example=Size(
            size_type=SizeType.DIAMETER,
            nominal_size=Decimal("10"),
            tolerance=None,
            unit=Unit.MILLIMETER,
        ),
    )
    depth: Size = Field(
        ...,
        description="The depth of the bore.",
        example=Size(
            size_type=SizeType.LINEAR,
            nominal_size=Decimal("50"),
            tolerance=None,
            unit=Unit.MILLIMETER,
        ),
    )
    thread: Optional[Thread] = Field(
        None, description="The threaded feature within the bore, if applicable."
    )


class RoughnessWaviness(BaseModel):
    """
    Represents the waviness characteristics of a surface in terms of height and width.

    Attributes:
    ----------
    - height (Size): The height of the waviness, typically measured as the peak-to-valley distance.
    - width (Size): The width of the waviness, representing the wavelength or distance between peaks.
    """

    height: Size = Field(
        ...,
        description="The height of the waviness, typically measured as the peak-to-valley distance.",
    )
    width: Size = Field(
        ...,
        description="The width of the waviness, representing the wavelength or distance between peaks.",
    )


class RoughnessEvaluationLength(BaseModel):
    """For sophisticated application, the sample needs
    to be taken over a longer distances. This is specified the
    either the sampling length in millimeter (ISO 3012:1974,
    ISO 3012:1978, ISO 3012:1992) or as multiple of the main lambda
    (ISO 3012:2002 and ISO 3012:2021).


    Attributes:
    ----------
    - length: evaluation length in the specified units.
    - lambda_c_multiple: multiple of the main cutoff lambda_c
    """

    length: Optional[Size]
    lambda_c_multiple: Optional[Decimal]


class RoughnessCondition(BaseModel):
    """
    Represents a condition for surface roughness specified on a technical drawing.

    Attributes:
    ----------
    - condition_type (RoughnessConditionType): Specifies whether the condition applies
      to the upper limit, lower limit, or average of the roughness.
    - filter_type (RoughnessFilterType): The filter used during roughness measurement.
    - lambda_s (Optional[Size]): The short wavelength cutoff for filtering.
    - lambda_c (Optional[Size]): The long wavelength cutoff for filtering.
    - parameter (RoughnessParameter): The roughness parameter being evaluated (e.g., Ra, Rz).
    - evaluation_length (RoughnessEvaluationLength): Details of the evaluation length
      used for the roughness measurement.
    - acceptance_criterion (RoughnessAcceptanceCriterion): Specifies the acceptance rule
      for the roughness condition (e.g., 16%-rule, maximum, mean).
    - value (Size): The target roughness value specified.
    - roughness_grade (Optional[str]): An optional roughness grade (e.g., N6, N7)
      associated with the condition.
    """

    condition_type: RoughnessConditionType = Field(
        ...,
        description="Specifies whether the condition applies to the upper limit, lower limit, or average of the roughness.",
    )
    filter_type: RoughnessFilterType = Field(
        ...,
        description="The filter used during roughness measurement (e.g., Gaussian, Spline).",
    )
    lambda_s: Optional[Size] = Field(
        None,
        description="The short wavelength cutoff for filtering, if specified.",
    )
    lambda_c: Optional[Size] = Field(
        None,
        description="The long wavelength cutoff for filtering, if specified.",
    )
    parameter: RoughnessParameter = Field(
        ...,
        description="The roughness parameter being evaluated (e.g., Ra, Rz, Rt).",
    )
    evaluation_length: RoughnessEvaluationLength = Field(
        ...,
        description="Details of the evaluation length used for roughness measurement.",
    )
    acceptance_criterion: RoughnessAcceptanceCriterion = Field(
        ...,
        description="Specifies the acceptance rule for the roughness condition (e.g., 16%-rule, maximum, mean).",
    )
    value: Size = Field(
        ...,
        description="The target roughness value specified in the condition.",
    )
    roughness_grade: Optional[str] = Field(
        None,
        description="An optional roughness grade (e.g., N6, N7) associated with the condition.",
        example="N6",
    )


class Roughness(BaseModel):
    """
    Represents the roughness specifications on a technical drawing.

    Attributes:
    ----------
    - standard (RoughnessStandard): The standard used for defining the roughness specifications
      (e.g., ISO 1302:1992, ASME Y14.36M-1996).
    - machining_allowance (Optional[Size]): Additional material allowance for machining, if specified.
    - material_removal_type (RoughnessMaterialRemovalType): Indicates whether material removal is
      required, prohibited, or unspecified.
    - applies_all_around (bool): Indicates whether the roughness applies uniformly to the entire surface.
    - direction_of_lay (Optional[RoughnessDirectionOfLay]): Specifies the lay direction of the surface
      texture, if defined.
    - manufacturing_process (Optional[str]): A description of the manufacturing process that affects
      surface roughness, if provided.
    - conditions (List[RoughnessCondition]): A list of roughness conditions specifying upper, lower,
      or average limits for different parameters.
    - waviness (Optional[RoughnessWaviness]): Waviness specifications for the surface, if applicable.
    """

    standard: RoughnessStandard = Field(
        ...,
        description="The standard used for defining the roughness specifications (e.g., ISO 1302:1992, ASME Y14.36M-1996).",
    )
    machining_allowance: Optional[Size] = Field(
        None,
        description="Additional material allowance for machining, if specified.",
    )
    material_removal_type: RoughnessMaterialRemovalType = Field(
        ...,
        description="Indicates whether material removal is required, prohibited, or unspecified.",
    )
    applies_all_around: bool = Field(
        ...,
        description="Indicates whether the roughness applies uniformly to the entire surface.",
    )
    direction_of_lay: Optional[RoughnessDirectionOfLay] = Field(
        None,
        description="Specifies the lay direction of the surface texture, if defined (e.g., parallel, perpendicular).",
    )
    manufacturing_process: Optional[str] = Field(
        None,
        description="A description of the manufacturing process that affects surface roughness, if provided.",
    )
    conditions: list[RoughnessCondition] = Field(
        ...,
        description="A list of roughness conditions specifying upper, lower, or average limits for different parameters.",
    )
    waviness: Optional[RoughnessWaviness] = Field(
        None,
        description="Waviness specifications for the surface, if applicable.",
    )


class Process(Cue):
    """
    Represents a manufacturing process with its type, category, and source.

    Attributes:
    ----------
    - process_category (List[ProcessCategoryDIN8580]): One or more categories of processes based on DIN 8580.
    """

    callout_type: Literal[CueType.PROCESS] = CueType.PROCESS
    process_category: List[str] = Field(
        ...,
        description="The category of the process based on DIN 8580, e.g., forming or coating.",
        example=["SEPARATION", "CUTTING", "WATERJET_CUTTING"],
    )


class GDnTDatum(BaseModel):
    """
    Represents a GD&T datum definition.

    Attributes:
    ----------
    - blurb (str): Reference name of the datum. Typically includes a single
      character (e.g., "A") or a composite (e.g., "(A-B-C-D)[CM]").
    """

    blurb: str = Field(
        ...,
        description=(
            "Reference name of the datum. Examples: 'A', 'B', or composite names "
            "such as '(A-B-C-D)[CM]'."
        ),
    )


class GDnT(Cue):
    """
    Represents a GD&T (Geometric Dimensioning and Tolerancing) cue in a technical drawing.

    Attributes:
    ----------
    - characteristic (GDnTCharacteristic): The characteristic being controlled (e.g., flatness, circularity).
    - zone (Size): The tolerance zone defined for the characteristic.
    - zone_combinations (List[GDnTZoneCombination]): Specifies if the zones are combined or separated.
    - zone_offset (Optional[str]): Offset for the tolerance zone, if applicable.
    - zone_constraint (Optional[GDnTZoneConstraint]): Constraints on the tolerance zone (e.g., orientation only).
    - feature_filter_type (Optional[GDnTFilterType]): The type of filter applied to the feature.
    - associated_feature (Optional[GDnTAssociatedFeature]): Specifies the feature association (e.g., Gaussian, minimax).
    - derived_feature (Optional[GDnTDerivedFeature]): Indicates if the feature is derived (e.g., projected or mean).
    - associated_reference (Optional[GDnTAssociatedReference]): Reference for associating elements in tolerance evaluation.
    - reference_parameter (Optional[GDnTReferenceParameter]): Parameter of the reference element (e.g., peak value, deviation span).
    - material_condition (Optional[GDnTMaterialCondition]): Material condition (e.g., maximum material condition).
    - state (Optional[GDnTState]): State of the feature (e.g., free state).
    - datums (List[GDnTDatum]): List of datums used as references for the GD&T characteristic.
    """

    characteristic: GDnTCharacteristic = Field(
        ...,
        description="The GD&T characteristic being controlled (e.g., flatness, circularity).",
    )
    zone: Size = Field(
        ..., description="The tolerance zone defined for the characteristic."
    )
    zone_combinations: list[GDnTZoneCombination] = Field(
        default_factory=list,
        description="Specifies if the zones are combined or separated.",
    )
    zone_offset: Optional[str] = Field(
        None, description="Offset for the tolerance zone, if applicable."
    )
    zone_constraint: Optional[GDnTZoneConstraint] = Field(
        None, description="Constraints on the tolerance zone (e.g., orientation only)."
    )
    feature_filter_type: Optional[GDnTFilterType] = Field(
        None, description="The type of filter applied to the feature."
    )
    associated_feature: Optional[GDnTAssociatedFeature] = Field(
        None, description="Specifies the feature association (e.g., Gaussian, minimax)."
    )
    derived_feature: Optional[GDnTDerivedFeature] = Field(
        None,
        description="Indicates if the feature is derived (e.g., projected or mean).",
    )
    associated_reference: Optional[GDnTAssociatedReference] = Field(
        None, description="Reference for associating elements in tolerance evaluation."
    )
    reference_parameter: Optional[GDnTReferenceParameter] = Field(
        None,
        description="Parameter of the reference element (e.g., peak value, deviation span).",
    )
    material_condition: Optional[GDnTMaterialCondition] = Field(
        None, description="Material condition (e.g., maximum material condition)."
    )
    state: Optional[GDnTState] = Field(
        None, description="State of the feature (e.g., free state)."
    )
    datums: list[GDnTDatum] = Field(
        default_factory=list,
        description="List of datums used as references for the GD&T characteristic.",
    )


class GeometricShapeCuboid(BaseModel):
    """
    Represents the dimensions of a cuboid shape.

    Attributes:
    ----------
    - width (Size): Width of the cuboid.
    - height (Size): Height of the cuboid.
    - depth (Size): Depth of the cuboid.
    """

    width: Size
    height: Size
    depth: Size


class GeometricShapeCylinder(BaseModel):
    """
    Represents the dimensions of a cylindrical shape.

    Attributes:
    ----------
    - diameter (Size): Diameter of the cylinder.
    - height (Size): Height of the cylinder.
    """

    diameter: Size
    height: Size


class Geometry(BaseModel):
    """
    Base class for representing geometric shapes.

    Attributes:
    ----------
    - base_geometry_type (BaseGeometryType): The type of the base geometry (e.g., PLATE, BLOCK, ROD).
    """

    geometry_type: GeometryType


class GeometryBlock(Geometry):
    """
    Represents the geometry of a block-shaped material.

    Attributes:
    ----------
    - base_geometry_type (Literal[BaseGeometryType.BLOCK]): Specifies the shape as a block.
    - cuboid (GeometricShapeCuboid): Dimensions of the block as a cuboid.
    """

    geometry_type: Literal[GeometryType.BLOCK] = GeometryType.BLOCK
    cuboid: GeometricShapeCuboid


class GeometryPlate(Geometry):
    """
    Represents the geometry of a plate-shaped material.

    Attributes:
    ----------
    - base_geometry_type (Literal[BaseGeometryType.PLATE]): Specifies the shape as a plate.
    - cuboid (GeometricShapeCuboid): Dimensions of the plate as a cuboid.
    """

    geometry_type: Literal[GeometryType.PLATE] = GeometryType.PLATE
    cuboid: GeometricShapeCuboid


class BaseGeometryRod(Geometry):
    """
    Represents the geometry of a rod-shaped material.

    Attributes:
    ----------
    - base_geometry_type (Literal[BaseGeometryType.ROD]): Specifies the shape as a rod.
    - cylinder (GeometricShapeCylinder): Dimensions of the rod as a cylinder.
    """

    base_geometry_type: Literal[GeometryType.ROD] = GeometryType.ROD
    cylinder: GeometricShapeCylinder


class Material(BaseModel):
    blurb: str
    raw_ocr_blurb: str
    standard: str
    designation: str
    material_category: tuple[
        Optional[MaterialCategory1],
        Optional[MaterialCategory2],
        Optional[MaterialCategory3],
    ]


class MaterialCombination(Cue):
    materials: list[Material]


class BillOfMaterialRow(BaseModel):
    """Row of a BOM table

    Attributes:
    ----------
    - serial (Optional[str]): Serial number or Item Number,
      giving the serial number used in BOM table.
    - position (Optional[str]): Position Number of the part
      on the assembly is defined using position bubbles.
      This position number is mentioned on the BOM table.
    - quantity (Optional[W24PhysicalQuantity]): Quantity of the part is defined
      as Physical Quantity with a value, unit and tolerance.
    - part_number (Optional[str]): Part Number of the parts
      listed in the bill of material.
    - designation (Optional[str]): Designation/Title of the part
      listed in the bill of material.
    - material (list[MaterialCombination]): Material of the part listed in the
      bill of material. These materials could be optional
      set of material that could be applicable for the part.
      For example: Either (Material_A and Material_B)
        Or (Material_C and Material_D)
        Here,
        (Material_A and Material_B) is a material set
        (Material_C and Material_D) is another material set
    - weight (Optional[Quantity]): Weight of the parts listed in the bill of
        material.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    serial: Optional[str]
    position: Optional[str]
    quantity: Optional[Quantity] = Field(
        None, description="Physical quantity in the string format of Pint."
    )
    part_number: Optional[str]
    designation: Optional[str]
    material_options: list[MaterialCombination]
    weight: Optional[Quantity] = None


class BillOfMaterial(BaseModel):
    rows: list[BillOfMaterialRow] = Field(
        ...,
        description="List of rows in the bill of material.",
    )


class RevisionTableRow(BaseModel):
    """
    Represents a single row in a revision table, documenting changes made
    to a drawing or technical document.

    Attributes:
    ----------
    - revision_serial (Optional[str]):  Serial number used to identify the revision.
      Often referred to as Index or Position in the table (e.g., "A", "B", "C",
      or "01", "02", "03").
    - description (str): Description of the change or revision made.
    - revision_date (Optional[date]): The date when the revision was made.
    """

    revision_serial: Optional[str] = Field(
        None,
        description=(
            "Serial number used to identify the revision, typically indicated by "
            "letters (e.g., 'A', 'B') or numbers (e.g., '01', '02')."
        ),
        example="A",
    )

    description: str = Field(
        ...,
        description="Description of the change or revision made.",
        example="Added dimension to part edge.",
    )

    revision_date: Optional[date] = Field(
        None,
        description="The date when the revision was implemented.",
        example="2025-01-24",
    )


class RevisionTable(BaseModel):
    rows: list[RevisionTableRow] = Field(
        ...,
        description="List of rows in the revision table.",
    )


class Cue(BaseModel):
    """
    Base class for callout objects in technical drawings.
    """

    blurb: Optional[str] = Field(
        None,
        description="Optional human-readable text providing additional details about the callout.",
    )


class Note(Cue):
    """
    Represents a note in a technical drawing.

    Attributes:
    ----------
    - note_type (NoteType): The type of note, differentiating between canvas,
        sectional, or sectional callouts.
    """

    note_type: NoteType = Field(
        ...,
        description=(
            "The type of the note, specifying whether it is a canvas note, sectional note, "
            "or a sectional callout."
        ),
    )


class Doubt(Cue):
    """
    Represents a doubt or ambiguity identified by the system in the technical drawing.

    This class inherits the structure of a `Callout` but is specifically used
    to highlight potential issues or uncertainties detected by Werk24 during the
    interpretation of the drawing.

    Note:
        The `Doubt` class does not introduce additional attributes beyond those
        defined in the `Callout` base class.
    """

    pass


class Radius(Cue):
    quantity: Decimal
    curvature_type: Optional[CurvatureType] = None
    size: Size


class ToleratedQuantity(BaseModel):
    """
    Represents a quantity with an associated tolerance.

    Attributes:
    ----------
    - quantity (Quantity) The main quantity value.
    - tolerance (Tolerance): The allowed variation for the quantity.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)
    quantity: Quantity = Field(..., description="The main quantity value.")
    tolerance: Tolerance = Field(
        ..., description="The allowed variation for the quantity."
    )
