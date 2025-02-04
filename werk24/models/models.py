import abc
from datetime import date
from decimal import Decimal
from enum import Enum
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple, Union

from pydantic import (
    UUID4,
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    Json,
    ValidationError,
    ValidationInfo,
    field_validator,
)

from werk24._version import __version__

from .enums import (
    CoordinateSpace,
    CurvatureType,
    DepthType,
    GDnTAssociatedFeature,
    GDnTCharacteristic,
    GDnTDerivedFeature,
    GDnTMaterialCondition,
    GDnTReferenceAssociation,
    GDnTReferenceParameter,
    GDnTState,
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
    PageType,
    ProjectionMethodType,
    RedactionZoneType,
    RoughnessAcceptanceCriterion,
    RoughnessConditionType,
    RoughnessDirectionOfLay,
    RoughnessFilterType,
    RoughnessMaterialRemovalType,
    RoughnessParameter,
    RoughnessStandard,
    SizeType,
    TechreadExceptionLevel,
    ThreadHandedness,
    ThreadType,
    UnitSystemType,
    VolumeEstimateType,
)
from .v1.ask import W24Ask, W24AskResponse, W24AskType, deserialize_ask_response

ALLOWED_CALLBACK_HEADERS = {"authorization"}


class Confidence(BaseModel):
    """
    Represents a confidence score for a feature or measurement.

    Attributes:
    ----------
    - score (Decimal): The confidence score of the feature, indicating the confidence the symstem has in the reading.
    """

    score: Decimal = Field(
        ...,
        description="The confidence score of the feature, indicating the confidence the symstem has in the reading.",
        example=Decimal("0.75"),
    )


class Quantity(BaseModel):
    value: Decimal
    unit: str


class Reference(BaseModel):
    """
    Represents a general information entry.

    Attributes:
    ----------
    - language (Optional[Language]): The language of the information, if known.
    - value (str): The text value of the information.
    """

    reference_id: int


class Weight(Quantity, Reference):
    pass


class Entry(Reference):

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


class GeneralTolerances(Reference):
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

    principle: Optional[GeneralTolerancesPrinciple] = Field(
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


class Feature(Reference):
    """
    Represents a design or manufacturing cue with descriptive information and metadata.

    Attributes:
    ----------
    - label (str): A short description or note associated with the cue.
    - confidence (Confidence): The confidence in the feature extraction or interpretation.
    """

    label: str  # Description or explanation of the cue
    confidence: Optional[Confidence] = Field(
        ...,
        description="Confidence in the feature extraction or interpretation.",
    )


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
    - is_approximation (bool): Indicates whether the tolerance is an approximation (e.g., 'approx. 5').
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

    is_general_tolerance: bool = Field(
        False,
        description="Whether the general tolerance was applied to this dimension.",
        example=True,
    )

    is_approximation: bool = Field(
        False,
        description="Whether the tolerance is an approximation (e.g., 'approx. 5').",
    )


class Size(Quantity):
    """
    Represents a size definition for a part or feature in an engineering context.

    Attributes:
    ----------
    - size_type (SizeType): The type of size (e.g., diameter, linear, angular) as defined by `SizeType`.
    - tolerance (Tolerance): The tolerance specifications associated with this size.
        If no tolerance is set, the general tolerance applies.
    """

    size_type: SizeType = Field(
        ...,
        description="The type of size (e.g., diameter, linear, angular).",
        example=SizeType.DIAMETER,
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


class Depth(BaseModel):
    """
    Represents the depth of a feature, such as a hole or bore.

    Attributes:
    ----------
    - depth (Decimal): The depth of the feature.
    """

    depth_type: DepthType
    size: Optional[Size]


class Dimension(Feature):
    """
    Represents a measurement cue in an engineering or technical drawing.

    Attributes:
    ----------
    - quantity (Decimal): The quantity or value associated with the measurement (e.g., length, diameter).
    - size (Size): The size details including size type, nominal size, tolerance, and unit.
    """

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


class ThreadSpacing(BaseModel):
    pitch_in_mm: Decimal = Field(
        ...,
        description="The pitch of the thread, defining the distance between thread crests.",
    )

    threads_per_inch: Decimal = Field(
        ...,
        ge=0,
        description="The number of threads per inch (TPI) for imperial threads. Must be non-negative.",
        example=Decimal("20"),
    )


class Thread(Feature):
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

    spacing: ThreadSpacing = Field(
        ...,
        description="The spacing of the thread, defining the distance between thread crests.",
    )

    handedness: ThreadHandedness = Field(
        ..., description="The direction of the thread, such as LEFT or RIGHT."
    )

    length: Optional[Size] = Field(
        default=None,
        description="The length of the threaded feature, including nominal size and tolerances.",
    )


class ThreadISOMetric(Thread):
    """
    Represents an ISO Metric thread.

    Attributes:
    ----------
    - female_major_diameter_tolerance (Tolerance): Tolerance for the major diameter of female threads.
    - female_pitch_diameter_tolerance (Tolerance): Tolerance for the pitch diameter of female threads.
    - male_major_diameter_tolerance (Tolerance): Tolerance for the major diameter of male threads.
    - male_pitch_diameter_tolerance (Tolerance): Tolerance for the pitch diameter of male threads.
    """

    thread_type: Literal[ThreadType.ISO_METRIC] = ThreadType.ISO_METRIC
    female_major_diameter_tolerance: Optional[Tolerance]
    female_pitch_diameter_tolerance: Optional[Tolerance]
    male_major_diameter_tolerance: Optional[Tolerance]
    male_pitch_diameter_tolerance: Optional[Tolerance]


class ThreadSM(Thread):
    """
    Represents a screw machine (SM) thread.

    Attributes:
    ----------
    - sm_size (Decimal): The size of the SM thread.
    """

    thread_type: Literal[ThreadType.SM] = ThreadType.SM
    sm_size: Decimal


class ThreadUTS(Thread):
    """
    Represents a Unified Thread Standard (UTS) thread.

    Attributes:
    ----------
    - uts_size (str): The size designation of the UTS thread (e.g., '1/4', '1/2').
    - uts_series (str): The series designation of the UTS thread (e.g., 'UNC', 'UNF').
    - tolerance_class (str): The tolerance class for the UTS thread (e.g., '2A', '3B').
    """

    thread_type: Literal[ThreadType.UTS] = ThreadType.UTS
    uts_size: str
    uts_series: str
    uts_tolerance_class: str


class ThreadACME(Thread):
    """
    Represents an ACME thread.

    Attributes:
    ----------
    - acme_size (str): The nominal size of the ACME thread.
    - acme_series (str): The series designation of the ACME thread.
    """

    thread_type: Literal[ThreadType.ACME] = ThreadType.ACME
    acme_size: str
    acme_series: str


class ThreadNPT(Thread):
    """American National Standard Pipe Thread standards,
        often called National Pipe Thread (NPT) standards.
    * NPT - National pipe taper
    * NPS - National pipe straight

    Attributes:
    ----------
    - npt_size: NPT size as string representation.
      Threads diameter in inch are represented as decimal or fractions
      with a tailing '"'
      Examples: 2", 1 3/4"
    - npt_series (str): NPT series following ANSI B 1.20.1.
      Valid values include NPT, NPTF, NPSC, NPSF, NPSL, NPSM
    """

    thread_type: Literal[ThreadType.NPT] = ThreadType.NPT
    npt_size: str
    npt_series: str


class ThreadWhitworth(Thread):
    """
    Represents a Whitworth thread.

    Attributes:
    ----------
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
    - knuckle_size (str): The nominal size of the Knuckle thread.
    - knuckle_series (str): The series designation of the Knuckle thread.
    - knuckle_profile (Optional[Fraction]): The profile of the Knuckle thread, represented as a fraction.
    """

    thread_type: Literal[ThreadType.KNUCKLE] = ThreadType.KNUCKLE
    knuckle_size: str
    knuckle_series: str
    knuckle_profile: Optional[str]


ThreadUnion = Union[
    ThreadISOMetric,
    ThreadSM,
    ThreadUTS,
    ThreadACME,
    ThreadWhitworth,
    ThreadKnuckle,
    ThreadNPT,
]


class Chamfer(Feature):
    """
    Represents a chamfer feature in an engineering or technical drawing.

    Attributes:
    ----------
    - size (Size): The linear size of the chamfer (e.g., the width or depth of the chamfer).
    - angle (Size): The angle of the chamfer, typically in degrees (e.g., 45°).
    """

    quantity: int = Field(
        ...,
        ge=1,
        description="The number of chamfers or instances. Must be at least 1.",
    )

    size: Size = Field(
        ...,
        description="The linear size of the chamfer, such as the width or depth.",
        example=Size(
            size_type=SizeType.LINEAR,
            value=Decimal("2"),
            tolerance=Tolerance(
                tolerance_grade="IT7",
                deviation_lower=Decimal("-0.1"),
                deviation_upper=Decimal("0.1"),
                fit=None,
                is_theoretically_exact=False,
                is_reference=False,
                is_approximation=False,
            ),
            unit="millimeter",
        ),
    )

    angle: Size = Field(
        ...,
        description="The angle of the chamfer, typically specified in degrees.",
        example=Size(
            size_type=SizeType.ANGULAR,
            value=Decimal("45"),
            tolerance=Tolerance(
                tolerance_grade="IT8",
                deviation_lower=Decimal("-0.5"),
                deviation_upper=Decimal("0.5"),
                fit=None,
                is_theoretically_exact=False,
                is_reference=False,
                is_approximation=False,
            ),
            unit="degree",
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
            value=Decimal("10"),
            tolerance=Tolerance(
                tolerance_grade="IT7",
                deviation_lower=Decimal("-0.1"),
                deviation_upper=Decimal("0.1"),
                fit=None,
                is_theoretically_exact=False,
                is_reference=False,
            ),
            unit="millimeter",
        ),
    )
    depth: Depth = Field(
        ...,
        description="The depth of the counterbore.",
        example=Size(
            size_type=SizeType.LINEAR,
            value=Decimal("5"),
            tolerance=Tolerance(
                tolerance_grade="IT8",
                deviation_lower=Decimal("-0.2"),
                deviation_upper=Decimal("0.2"),
                fit=None,
                is_theoretically_exact=False,
                is_reference=False,
            ),
            unit="millimeter",
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
            value=Decimal("15"),
            tolerance=None,
            unit="millimeter",
        ),
    )
    angle: Size = Field(
        ...,
        description="The angle of the countersink, typically in degrees.",
        example=Size(
            size_type=SizeType.ANGULAR,
            value=Decimal("90"),
            tolerance=None,
            unit="degree",
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
            value=Decimal("8"),
            tolerance=None,
            unit="millimeter",
        ),
    )
    depth: Depth = Field(
        ...,
        description="The depth of the counterdrill.",
        example=Size(
            size_type=SizeType.LINEAR,
            value=Decimal("20"),
            tolerance=None,
            unit="millimeter",
        ),
    )
    angle: Optional[Size] = Field(
        ...,
        description="The angle of the counterdrill, typically in degrees.",
        example=Size(
            size_type=SizeType.ANGULAR,
            value=Decimal("118"),
            tolerance=None,
            unit="degree",
        ),
    )


class Bore(Feature):
    """
    Represents a bore feature in an engineering or technical drawing.

    Attributes:
    ----------
    - quantity (Decimal): The number of bores or instances.
    - counterbore (Optional[Counterbore]): The counterbore feature, if present.
    - countersink (Optional[Countersink]): The countersink feature, if present.
    - counterdrill (Optional[Counterdrill]): The counterdrill feature, if present.
    - diameter (Size): The diameter of the bore.
    - depth (Size): The depth of the bore.
    - thread (Optional[Thread]): The threaded feature within the bore, if applicable.
    """

    quantity: int = Field(
        ...,
        ge=1,
        description="The number of bores or instances. Must be at least 1.",
        example=2,
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
            value=Decimal("10"),
            tolerance=None,
            unit="millimeter",
        ),
    )
    depth: Optional[Depth] = Field(
        ...,
        description="The depth of the bore.",
        example=Depth(
            size=Size(
                size_type=SizeType.LINEAR,
                value=Decimal("50"),
                tolerance=None,
                unit="millimeter",
            ),
            depth_type=DepthType.SIZE,
        ),
    )
    thread: Optional[Reference] = Field(
        None, description="Reference to the reference_id of the associated thread."
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

    model_config = ConfigDict(arbitrary_types_allowed=True)

    condition_type: Optional[RoughnessConditionType] = Field(
        ...,
        description="Specifies whether the condition applies to the upper limit, lower limit, or average of the roughness.",
    )
    filter_type: Optional[RoughnessFilterType] = Field(
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
    parameter: Optional[RoughnessParameter] = Field(
        ...,
        description="The roughness parameter being evaluated (e.g., Ra, Rz, Rt).",
    )
    evaluation_length: Optional[Quantity] = Field(
        None,
        description="Details of the evaluation length used for roughness measurement.",
    )
    acceptance_criterion: Optional[RoughnessAcceptanceCriterion] = Field(
        ...,
        description="Specifies the acceptance rule for the roughness condition (e.g., 16%-rule, maximum, mean).",
    )
    value: Optional[Size] = Field(
        ...,
        description="The target roughness value specified in the condition.",
    )
    roughness_grade: Optional[str] = Field(
        None,
        description="An optional roughness grade (e.g., N6, N7) associated with the condition.",
        example="N6",
    )


class Roughness(Feature):
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


class SecondaryProcess(Feature):
    """
    Represents a manufacturing process with its type, category, and source.

    Attributes:
    ----------
    - process_category (List[ProcessCategoryDIN8580]): One or more categories of processes based on DIN 8580.
    """

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
    - label (str): Reference name of the datum. Typically includes a single
      character (e.g., "A") or a composite (e.g., "(A-B-C-D)[CM]").
    """

    label: str = Field(
        ...,
        description=(
            "Reference name of the datum. Examples: 'A', 'B', or composite names "
            "such as '(A-B-C-D)[CM]'."
        ),
    )


class GDnTExtend(Size):
    quantity: int = 1
    angle: Optional[Decimal] = None


class GDnTZone(BaseModel):
    """Preliminary defintion of the GDT Zone Value
    Future implementation will give access to the
    width and extend seperately

    Attributes:
    ----------
    value: Size
    extend: Optional[GDnTExtend] = None
    """

    value: Size
    extend: Optional[GDnTExtend] = None
    combination: Optional[str] = None
    offset: Optional[str] = None
    constraint: Optional[str] = None


class GDnTFeature(BaseModel):
    filter: Optional[str] = None
    associated_feature: Optional[GDnTAssociatedFeature] = None
    derived_feature: Optional[GDnTDerivedFeature] = None


class GDnTReference(BaseModel):
    association: Optional[GDnTReferenceAssociation] = Field(
        None, description="Reference for associating elements in tolerance evaluation."
    )
    parameter: Optional[GDnTReferenceParameter] = Field(
        None,
        description="Parameter of the reference element (e.g., peak value, deviation span).",
    )


class GDnT(Feature):
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
    - associated_reference (Optional[GDnTReferenceAssociation]): Reference for associating elements in tolerance evaluation.
    - reference_parameter (Optional[GDnTReferenceParameter]): Parameter of the reference element (e.g., peak value, deviation span).
    - material_condition (Optional[GDnTMaterialCondition]): Material condition (e.g., maximum material condition).
    - state (Optional[GDnTState]): State of the feature (e.g., free state).
    - datums (List[GDnTDatum]): List of datums used as references for the GD&T characteristic.
    """

    characteristic: GDnTCharacteristic = Field(
        ...,
        description="The GD&T characteristic being controlled (e.g., flatness, circularity).",
    )
    zone: Optional[GDnTZone] = Field(
        ..., description="The tolerance zone defined for the characteristic."
    )
    feature: Optional[GDnTFeature] = Field(
        ..., description="The feature being controlled by the GD&T characteristic."
    )
    reference: Optional[GDnTReference] = Field(
        ..., description="The reference for the GD&T characteristic."
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


class Geometry(BaseModel):
    """
    Base class for representing geometric shapes.

    Attributes:
    ----------
    - base_geometry_type (BaseGeometryType): The type of the base geometry (e.g., PLATE, BLOCK, ROD).
    """

    geometry_type: GeometryType


class GeometryCuboid(Geometry):
    """
    Represents the geometry of a cuboid

    Attributes:
    ----------
    - cuboid (GeometricShapeCuboid): Dimensions of the block as a cuboid.
    """

    geometry_type: Literal[GeometryType.CUBOID] = GeometryType.CUBOID
    width: Size
    height: Size
    depth: Size


class GeometryCylinder(Geometry):
    """
    Represents the geometry of a plate-shaped material.

    Attributes:
    ----------
    - base_geometry_type (Literal[BaseGeometryType.PLATE]): Specifies the shape as a plate.
    - cuboid (GeometricShapeCuboid): Dimensions of the plate as a cuboid.
    """

    geometry_type: Literal[GeometryType.CYLINDER] = GeometryType.CYLINDER
    diameter: Size
    depth: Size


class Material(BaseModel):
    raw_ocr: str
    standard: Optional[str]
    designation: str
    material_category: tuple[
        Optional[MaterialCategory1],
        Optional[MaterialCategory2],
        Optional[MaterialCategory3],
    ]


class MaterialCombination(Reference):
    material_combination: list[Material]


class BillOfMaterialRow(BaseModel):
    """Row of a BOM table

    Attributes:
    ----------
    - position (Optional[str]): Position Number of the part
      on the assembly is defined using position bubbles.
      This position number is mentioned on the BOM table.
    - part_number (Optional[str]): Part Number of the parts
      listed in the bill of material.
    - designation (Optional[str]): Designation/Title of the part
      listed in the bill of material.
    - material_options (list[MaterialCombination]): Material of the part
      listed in the bill of material. These materials could be optional
      set of material that could be applicable for the part.
      For example: Either (Material_A and Material_B)
        Or (Material_C and Material_D)
        Here,
        (Material_A and Material_B) is a material combination
        (Material_C and Material_D) is another material combination
    - quantity (Optional[W24PhysicalQuantity]): Quantity of the part is defined
      as Physical Quantity with a value, unit and tolerance.
    - weight (Optional[Quantity]): Weight of the parts listed in the bill of
        material.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    position: Optional[str]
    part_number: Optional[str]
    designation: Optional[str]
    material_options: list[MaterialCombination]
    quantity: Optional[Quantity] = Field(
        None, description="Physical quantity in the string format of Pint."
    )
    unit_weight: Optional[Quantity] = None


class BillOfMaterial(Reference):
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


class RevisionTable(Reference):
    rows: list[RevisionTableRow] = Field(
        ...,
        description="List of rows in the revision table.",
    )


class Note(Feature):
    """
    Represents a note in a technical drawing.

    Attributes:
    ----------
    - note_type (NoteType): The type of note, differentiating between canvas,
        sectional, or sectional features.
    """

    note_type: NoteType = Field(
        ...,
        description=(
            "The type of the note, specifying whether it is a canvas note, sectional note, "
            "or a sectional feature."
        ),
    )


class Radius(Feature):
    quantity: int
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


class UnitSystem(Reference):
    primary_unit_system: Optional[UnitSystemType]
    secondary_unit_system: Optional[UnitSystemType]


class ProjectionMethod(Reference):
    """Projection Method according to ISO 128"""

    projection_method: ProjectionMethodType


class CuttingProcess(BaseModel):
    requires_bending: Optional[bool]
    output_geometry: Optional[GeometryCuboid]


class TurningProcess(BaseModel):
    requires_secondary_milling: bool
    output_geometry: Optional[GeometryCylinder]


class MillingProcess(BaseModel):
    axis_count: Optional[int]
    output_geometry: Optional[GeometryCuboid]


PrimaryProcessUnion = Union[CuttingProcess, TurningProcess, MillingProcess]


class Polygon(BaseModel):
    coordinate_space: CoordinateSpace
    coordinates: list[tuple[int, int]]


class VolumeEstimate(Quantity):
    volume_estimate_type: VolumeEstimateType


class ReferencePosition(BaseModel):
    reference_id: int
    polygon: Optional[Polygon]


class AskType(str, Enum):
    """The type of request to be sent to the server."""

    REFERENCE_POSITIONS = "REFERENCE_POSITIONS"
    CUSTOM = "CUSTOM"
    FEATURES = "FEATURES"
    INSIGHTS = "INSIGHTS"
    META_DATA = "META_DATA"
    REDACTION = "REDACTION"
    SHEET_IMAGE = "SHEET_IMAGE"
    VIEW_IMAGE = "VIEW_IMAGE"


class AskV2(BaseModel):
    """A class that represents a request for information
    from the server.
    """

    ask_version: Literal["v2"] = "v2"


Ask = Union[W24Ask, "AskV2"]


class AskReferencePositions(AskV2):
    """Represents a request for the position of a component in the drawing."""

    ask_type: Literal[AskType.REFERENCE_POSITIONS] = AskType.REFERENCE_POSITIONS


class Answer(BaseModel, abc.ABC):
    """
    A class that represents an answer to a request from the server.

    """

    ask_version: Literal["v2"] = "v2"


class AnswerFeaturesMiscallaneous(Answer):
    ask_type: Literal[AskType.FEATURES] = AskType.FEATURES
    page_type: Literal[PageType.MISCELLANEOUS] = PageType.MISCELLANEOUS


class AnswerFeaturesMechanicalComponent(Answer):
    """
    Represents an answer to a request for features of a mechanical component drawing from the server.

    Attributes:
    ----------
    - dimensions (List[Dimension]): Dimension details for the component.
    - threads (List[Thread]): Thread specifications for the component.
    - bores (List[Bore]): Bore specifications for the component.
    - chamfers (List[Chamfer]): Chamfer specifications for the component.
    - roughnesses (List[Roughness]): Additional surface roughness details beyond general roughness.
    - gdnts (List[GDnT]): Geometric dimensioning and tolerancing (GD&T) details.
    - radii (List[Radius]): Radius specifications for the component.
    """

    ask_type: Literal[AskType.FEATURES] = AskType.FEATURES
    page_type: Literal[PageType.COMPONENT_DRAWING] = PageType.COMPONENT_DRAWING

    dimensions: List[Dimension] = Field(
        default_factory=list,
        description="Dimension details for the component.",
    )
    threads: List[ThreadUnion] = Field(
        default_factory=list,
        description="Thread specifications for the component.",
    )
    bores: List[Bore] = Field(
        default_factory=list,
        description="Bore specifications for the component.",
    )
    chamfers: List[Chamfer] = Field(
        default_factory=list,
        description="Chamfer specifications for the component.",
    )
    roughnesses: List[Roughness] = Field(
        default_factory=list,
        description="Additional surface roughness details beyond general roughness.",
    )
    gdnts: List[GDnT] = Field(
        default_factory=list,
        description="Geometric dimensioning and tolerancing (GD&T) details.",
    )
    radii: List[Radius] = Field(
        default_factory=list,
        description="Radius specifications for the component.",
    )


class AnswerReferencePositions(Answer):
    """
    A class that represents an answer to a request for the position of a component in the drawing.

    Attributes:
    ----------
    - reference_positions (List[ReferencePosition]): The positions of the component in the drawing.
    """

    ask_type: Literal[AskType.REFERENCE_POSITIONS] = AskType.REFERENCE_POSITIONS

    reference_positions: list[ReferencePosition] = Field(
        ..., description="The positions of the component in the drawing."
    )


class AnswerInsightsMechanicalComponent(Answer):
    ask_type: Literal[AskType.INSIGHTS] = AskType.INSIGHTS
    page_type: Literal[PageType.COMPONENT_DRAWING] = PageType.COMPONENT_DRAWING

    primary_process_options: List[PrimaryProcessUnion] = Field(
        ...,
        description="The primary processing options available for the component.",
    )

    secondary_processes: List[SecondaryProcess] = Field(
        ...,
        description="The final geometry or shape of the material after processing.",
    )

    volume_estimate: Optional[VolumeEstimate] = Field(
        None,
        description="The estimated volume of the component.",
    )


class AskMetaData(AskV2):
    """A class that represents a request for metadata
    from the server.
    """

    ask_type: Literal[AskType.META_DATA] = AskType.META_DATA


class AnswerMetaDataMiscellaneous(Answer):
    """
    A class that represents an answer to for a page that is NOT a component drawing.
    """

    ask_type: Literal[AskType.META_DATA] = AskType.META_DATA
    page_type: Literal[PageType.MISCELLANEOUS] = PageType.MISCELLANEOUS


class AnswerMetaDataMechanicalComponent(Answer):
    """A class that represents an answer to a request for metadata of a mechanical component drawing from the server.

    Attributes:
    ----------
    - identifiers (List[Identifier]): A list of identifiers associated with the component.
    - designation (List[Entry]): List of designations of the component in different languages.
    - languages (List[Language]): The languages used in the drawing.
    - general_tolerances (GeneralTolerances): General tolerance specifications.
    - general_roughness (Roughness): General roughness specifications.
    - material_options (List[MaterialCombination]): Material options for the component.
    - weight (Quantity): The weight of the component.
    - unit_system (UnitSystem): The units specification for the component.
    - bill_of_material (List[BillOfMaterialRow]): Bill of materials for the component.
    - revision_table (List[RevisionTableRow]): Revision history of the drawing.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    ask_type: Literal[AskType.META_DATA] = AskType.META_DATA
    page_type: Literal[PageType.COMPONENT_DRAWING] = PageType.COMPONENT_DRAWING

    identifiers: List[Identifier] = Field(
        default_factory=list,
        description="List of identifiers associated with the component.",
    )
    designation: list[Entry] = Field(
        default_factory=list,
        description="Designation of the component.",
    )
    languages: List[Language] = Field(
        default_factory=list,
        description="Languages used in the drawing.",
    )
    general_tolerances: Optional[GeneralTolerances] = Field(
        None,
        description="General tolerance specifications for the component.",
    )
    general_roughness: Optional[Roughness] = Field(
        None,
        description="General roughness specifications for the component.",
    )
    material_options: List[MaterialCombination] = Field(
        default_factory=list,
        description="Material options available for the component.",
    )
    weight: Optional[Weight] = Field(
        None,
        description="Weight of the component.",
    )
    projection_method: Optional[ProjectionMethod] = Field(
        None,
        description="Projection method used in the drawing (e.g., first angle or third angle).",
    )
    bill_of_material: Optional[BillOfMaterial] = Field(
        None,
        description="Bill of materials for the component, listing parts and quantities.",
    )
    unit_system: Optional[UnitSystem] = Field(
        None,
        description="The units specification for the component.",
    )


class AskFeatures(AskV2):
    """A class that represents a request for vallouts
    from the server.
    """

    ask_type: Literal[AskType.FEATURES] = AskType.FEATURES


class AskCustom(AskV2):
    ask_type: Literal[AskType.CUSTOM] = AskType.CUSTOM
    custom_id: str = Field(..., description="The ID of the custom output to request.")
    config: Dict[str, Any] = Field(
        {}, description="Configuration options for the custom output."
    )


class AskInsights(AskV2):
    """A class that represents a request for insights
    from the server.
    """

    ask_type: Literal[AskType.INSIGHTS] = AskType.INSIGHTS


class ThumbnailFileFormat(str, Enum):
    """The output format of the redacted drawing."""

    PDF = "PDF"
    PNG = "PNG"


class RedactionKeyword(BaseModel):
    keyword: str = Field(..., description="The keyword to redact from the drawing.")


class AskRedaction(AskV2):
    """
    A class that represents a request for redaction from the server.
    """

    ask_type: Literal[AskType.REDACTION] = AskType.REDACTION
    redact_logos: bool = Field(True, description="Redact the logos")
    redact_company_data: bool = Field(True, description="Redact company data")
    redact_personal_data: bool = Field(True, description="Redact personal data")
    redact_keywords: list[RedactionKeyword] = Field(
        [],
        description="List of Keywords to redact. Keywords are strings that should be redacted from the drawing.",
    )
    output_format: ThumbnailFileFormat = Field(
        ThumbnailFileFormat.PDF, description="Output format of the redacted drawing"
    )
    fill_color: str | None = Field(
        "#ffffff",
        description="Fill color for the redacted areas. Set to None if you only wish to obtain the redaction areas as polygons and perform the redaction on your end.",
    )


class RedactionZone(BaseModel):
    """
    A class that represents a redacted area in the drawing.

    Attributes:
    ----------
    - polygon(list[tuple[int,int]]): A list of x,y tuples representing the vertices of the redacted area.
    """

    redaction_zone_type: RedactionZoneType
    polygon: list[tuple[int, int]] = Field(
        ...,
        description="A list of x,y tuples representing the vertices of the redacted area.",
    )


class AnswerRedaction(Answer):
    """
    A class that represents an answer to a redaction request from the server.

    Attributes:
    ----------
    - redaction_zones (HttpUrl): A list of redacted areas in the drawing.
    """

    ask_type: Literal[AskType.REDACTION] = AskType.REDACTION

    redaction_zones: list[RedactionZone] = Field(
        ..., description="A list of redacted areas in the drawing."
    )


class AskSheetImage(AskV2):
    """Represents a request for a sheet image from the server."""

    ask_type: Literal[AskType.SHEET_IMAGE] = AskType.SHEET_IMAGE


class AskViewImage(AskV2):
    """Represents a request for a view image from the server."""

    ask_type: Literal[AskType.VIEW_IMAGE] = AskType.VIEW_IMAGE


def get_ask_subclasses() -> List:
    subclasses = AskV2.__subclasses__() + W24Ask.__subclasses__()
    # Recursively collect subclasses of subclasses, if any
    for subclass in subclasses:
        subclasses.extend(subclass.__subclasses__())
    return subclasses


def get_answer_subclasses() -> List:
    subclasses = Answer.__subclasses__()
    # Recursively collect subclasses of subclasses, if any
    for subclass in subclasses:
        subclasses.extend(subclass.__subclasses__())
    return subclasses


AskUnion = Union[tuple(get_ask_subclasses())]
ANSWER_SUBCLASSES = get_answer_subclasses()
AnswerUnion = Union[tuple(ANSWER_SUBCLASSES)]


class TechreadMessageType(str, Enum):
    """Message Type of the message that is sent
    from the server to the client in response to
    a request.
    """

    ASK = "ASK"
    PROGRESS = "PROGRESS"


class TechreadMessageSubtype(str, Enum):
    """Message Subtype for the MessageType: PROGRESS"""

    PROGRESS_COMPLETED = "COMPLETED"
    PROGRESS_INITIALIZATION_SUCCESS = "INITIALIZATION_SUCCESS"
    PROGRESS_STARTED = "STARTED"


class TechreadRequest(BaseModel):
    asks: List[AskUnion] = Field(..., description="List of asks")
    client_version: str = Field(default=__version__, description="Client version")
    max_pages: int = Field(..., ge=1, description="Maximum number of pages to process")


class TechreadAction(str, Enum):
    """List of supported actions by the Techread API"""

    INITIALIZE = "INITIALIZE"
    READ = "READ"


class Hook(BaseModel):
    """
    A Utility class to register callback requests for a specific message_type or W24Ask.

    The 'Hook' object is used for handling and maintaining callback requests. Registering
    an 'ask' should include a complete W24Ask definition, not just the ask type.

    Attributes:
    ----------
    message_type (Optional[W24TechreadMessageType]): Specifies the type of the message.
    message_subtype (Optional[W24TechreadMessageSubtype]): Specifies the subtype of the message.
    ask (Optional[W24Ask]): The complete definition of W24Ask, if any.
    function (Callable): The callback function to be invoked when the resulting information
        is available.

    Note:
    ----
    Either a message_type or an ask must be registered. Be careful when registering an ask;
    a complete W24Ask definition is required, not just the ask type.
    """

    message_type: Optional[TechreadMessageType] = None
    message_subtype: Optional[TechreadMessageSubtype] = None
    ask: Optional[AskUnion] = None
    function: Callable


class EncryptionKeys(BaseModel):
    """
    A class to hold the encryption keys for the client.

    Attributes:
    ----------
    public_key_pem (str): The public key in PEM format.
    private_key_pem (str): The private key in PEM format.
    """

    client_public_key_pem: bytes
    client_private_key_pem: bytes
    client_private_key_passphrase: Optional[bytes] = None


class TechreadExceptionType(str, Enum):
    """List of all the error types that can possibly
    be associated to the error type.
    """

    DRAWING_FILE_FORMAT_UNSUPPORTED = "DRAWING_FILE_FORMAT_UNSUPPORTED"
    """ The Drawing was submitted in a file format that is not supproted
    by the API at this stage.
    """

    DRAWING_FILE_SIZE_TOO_LARGE = "DRAWING_FILE_SIZE_TOO_LARGE"
    """ The Drawing file size exceeded the limit
    """

    DRAWING_RESOLUTION_TOO_LOW = "DRAWING_RESOLUTION_TOO_LOW"
    """ The resolution (dots per inch) was too low to be
    processed
    """

    DRAWING_CONTENT_NOT_UNDERSTOOD = "DRAWING_CONTENT_NOT_UNDERSTOOD"
    """ The file you submitted as drawing might not actually
    be a drawing
    """

    DRAWING_PAPER_SIZE_TOO_LARGE = "DRAWING_PAPER_SIZE_TOO_LARGE"
    """ The paper size is larger that the allowed paper size
    """


class TechreadException(BaseModel):
    """
    Error message that accompanies the W24TechreadMessage
    if an error occured.

    Attributes:
    ----------
    - exception_type (TechreadExceptionType): Error Type that allows the
        API-user to translate the message to a user-info.
    """

    exception_level: TechreadExceptionLevel
    exception_type: TechreadExceptionType


class TechreadBaseResponse(BaseModel):
    """
    BaseFormat for messages returned by the server.

    Attributes:
    ----------
    - exceptions (List[W24TechreadException]): List of exceptions
      that occured during the processing.
    """

    exceptions: List[TechreadException] = []

    @property
    def is_successful(self) -> bool:
        """Check whether an exception of the ERROR level was returned.

        Otherwise return True.

        Returns:
        -------
        - True if no exceptions occured,False otherwise.
        """
        return not self.exceptions


class PresignedPost(BaseModel):
    """
    Represents the details of a presigned POST request for uploading a file
    to the Werk24 file system.

    Attributes:
    ----------
    - url (HttpUrl): The URL where the POST request should be sent.
    - fields (Dict[str, str]): A dictionary of form fields to include in the POST request.
    """

    url: HttpUrl
    fields: Dict[str, str] = Field(alias="fields", default={})


class TechreadInitResponse(TechreadBaseResponse):
    """API response to the Initialize request

    Attributes:
    ----------
    - drawing_presigned_post: Presigned Post for uploading the drawing
    - model_presigned_post: Presigned Post for uploading the model
    - exceptions (List[W24TechreadException]): List of exceptions that occured
    """

    drawing_presigned_post: PresignedPost
    public_key: Optional[str] = None


class TechreadMessage(TechreadBaseResponse):
    """
    Represents a message sent from the server to the client.

    This class encapsulates the structure of a message that the server sends to
    the client, providing metadata and payload for processing.

    Attributes:
    ----------
    - request_id (UUID4): Unique identifier (UUID4) for the request, generated by
      the server.
    - message_type (TechreadMessageType): The main message type indicating the
      category of the message.
    - message_subtype (TechreadMessageSubtype): The subtype specifying additional
      details about the message.
    - page_number (int): The page number the message corresponds to (starting from 0).
    - payload_dict (Optional[AskResponse]): A dictionary containing the structured payload data.
    - payload_url (Optional[HttpUrl]): A URL for downloading binary data
      (e.g., images or large files).
    - payload_bytes (Optional[bytes]): Binary content downloaded from the `payload_url`.
      This wil initially be None, and will be populated when the client downloads the
      content from the `payload_url`. If you implement your own client, you need to
      download the content from the `payload_url` and set the `payload_bytes` attribute.
    """

    request_id: UUID4
    message_type: TechreadMessageType
    message_subtype: TechreadMessageSubtype | AskType | W24AskType
    page_number: int = 0
    payload_dict: Optional[
        AnswerUnion | TechreadInitResponse | W24AskResponse | dict
    ] = None
    payload_url: Optional[HttpUrl] = None
    payload_bytes: Optional[bytes] = None

    @field_validator("payload_dict", mode="before")
    def deserialize_payload(
        cls,
        v: Any,
        info: ValidationInfo,
    ) -> Optional[AnswerUnion | TechreadInitResponse | W24AskResponse | dict]:

        if v is None:
            return None

        # Progress Messages
        if (
            info.data["message_subtype"]
            == TechreadMessageSubtype.PROGRESS_INITIALIZATION_SUCCESS
        ):
            return TechreadInitResponse.model_validate(v)

        if v.get("ask_version") == "v2":
            for c_class in ANSWER_SUBCLASSES:
                try:
                    parsed = c_class.model_validate(v)
                    return parsed
                except ValidationError:
                    pass

        # V1 Asks
        return deserialize_ask_response(v, info)


class TechreadWithCallbackPayload(BaseModel):
    """
    Payload sent to the API to trigger a drawing read process with a callback URL.

    This class encapsulates the details required for initiating a drawing read request
    and registering a callback URL to receive the results.

    Attributes:
    ----------
    - asks (List[W24AskUnion]): List of asks specifying the required information.
    - callback_url (HttpUrl): The URL to call once processing is completed.
    - callback_headers (Optional[Dict[str, str]]): Headers to include with the callback
      request.
    - max_pages (int): Maximum number of pages to process. Defaults to 5.
    - client_version (str): The version of the client making the request.
    - public_key (Optional[str]): Public key for encrypting the callback payload,
      if applicable.
    """

    asks: List[AskUnion] = Field(
        default_factory=list,
        description="List of asks specifying the desired information to extract from the drawing.",
    )

    callback_url: HttpUrl = Field(
        ...,
        description="The URL to which the API will send the callback request after processing is completed.",
    )

    callback_headers: Optional[Dict[str, str]] = Field(
        default=None,
        description="Optional headers to include in the callback request. Headers must start with 'X-' or be whitelisted.",
    )

    max_pages: int = Field(
        ...,
        ge=1,
        description="Maximum number of pages to process. Must be at least 1.",
    )

    client_version: str = Field(
        default=__version__, description="Version of the client making the request."
    )
    public_key: Optional[str] = Field(
        default=None,
        description="Optional public key for encrypting the callback payload. Feature availability depends on the service level.",
    )

    @field_validator("callback_headers", mode="before")
    @classmethod
    def validate_callback_headers(
        cls,
        headers: Optional[Dict[str, str]],
        max_name_length: int = 128,
        max_value_length: int = 4096,
    ) -> Optional[Dict[str, str]]:
        """
        Validate the callback headers to ensure compliance with server-side constraints.

        Headers must:
        - Be either whitelisted (`authorization`) or prefixed with "X-".
        - Not exceed the maximum length for names and values.

        Args:
        ----
        - headers (Optional[Dict[str, str]]): The callback headers to validate.
        - max_name_length (int): Maximum allowed length for header names.
        - max_value_length (int): Maximum allowed length for header values.

        Returns:
        -------
        - Optional[Dict[str, str]]: The validated callback headers.

        Raises:
        ------
        - ValueError: If any header name or value violates the constraints.
        """
        if headers is None:
            return None

        for name, value in headers.items():
            # Validate header name
            if (
                name.lower() not in ALLOWED_CALLBACK_HEADERS
                and not name.lower().startswith("x-")
            ):
                raise ValueError(
                    f'Invalid header "{name}": must start with "X-" or be one of {ALLOWED_CALLBACK_HEADERS}.'
                )

            if len(name) > max_name_length:
                raise ValueError(
                    f'Header name "{name}" exceeds maximum length of {max_name_length} characters.'
                )

            # Validate header value
            if len(value) > max_value_length:
                raise ValueError(
                    f'Header value for "{name}" exceeds maximum length of {max_value_length} characters.'
                )

        return headers


class TechreadCommand(BaseModel):
    """Command that is sent from the client to the Server"""

    action: TechreadAction
    message: Json
