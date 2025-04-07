import abc
from datetime import date
from decimal import Decimal
from typing import List, Literal, Optional, Tuple, Union

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)

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
    PrimaryProcessType,
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
    ThreadHandedness,
    ThreadType,
    UnitSystemType,
    VolumeEstimateType,
)


class Confidence(BaseModel):
    """
    Represents a confidence score for a feature or measurement.
    """

    score: Decimal = Field(
        ...,
        description="The confidence score of the feature, indicating the confidence the symstem has in the reading.",
        examples=[Decimal("0.75")],
    )


class Quantity(BaseModel):
    """
    Represents a Physical Quantity with a value and a unit.
    """

    value: Decimal = Field(
        ...,
        description="The value of the quantity.",
        examples=[Decimal("10.5")],
        allow_inf_nan=True,  # Allowing inf for "R PLANE"
    )
    unit: str = Field(
        ...,
        description="The unit of the quantity.",
        examples=["mm"],
    )


class Reference(BaseModel):
    """
    Base model that allows refering to a specific object by its reference_id.
    """

    reference_id: int = Field(
        ...,
        description="Reference ID to identify the object.",
        examples=[12345],
    )


class Weight(Quantity, Reference):
    """
    Represents a weight value with a unit.
    """

    pass


class Entry(Reference):
    """
    Represents an entry in a list or table.
    """

    language: Optional[Language] = Field(
        None,
        description="The language of the identifier, if known.",
        examples=[Language.ENG, Language.DEU],
    )

    value: str = Field(
        ...,
        description="The value of the identifier. Must be a non-empty string.",
        examples=["12345-ABC"],
    )


class Identifier(Entry):
    """
    Represents an identifier (such as the drawing number) used for distinguishing elements in a drawing.
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
    """

    tolerance_standard: GeneralTolerancesStandard = Field(
        ...,
        description="The standard used for general tolerance definitions, e.g., DIN 7168 or ISO 2768.",
        examples=[GeneralTolerancesStandard.ISO_2768],
    )

    tolerance_class: Optional[str] = Field(
        ...,
        description="The tolerance class or grade, defined as a short string such as 'm', 'f', or 'c'.",
        examples=["m"],
    )

    principle: Optional[GeneralTolerancesPrinciple] = Field(
        ...,
        description="The principle governing the tolerance application, such as independence or envelope.",
        examples=[GeneralTolerancesPrinciple.INDEPENDENCE],
    )


class Balloon(Reference):
    """
    Represents a balloon annotation in a drawing or part diagram.
    """

    center: Tuple[int, int] = Field(
        ...,
        description="The (x, y) coordinates of the balloon's center on the diagram.",
        examples=[(150, 200)],
    )


class Feature(Reference):
    """
    Represents a design or manufacturing cue with descriptive information and metadata.
    """

    label: str = Field(
        ...,
        description="A short description of the feature in a human-readable format.",
    )

    confidence: Optional[Confidence] = Field(
        ...,
        description="Confidence in the feature extraction or interpretation.",
    )


class Tolerance(BaseModel):
    """
    Represents a tolerance specification for a part or feature.
    """

    tolerance_grade: Optional[str] = Field(
        None,
        description="The grade of tolerance, such as 'IT7' for an 'H7' fit. Calcuated if not specified.",
        examples=["IT7"],
    )

    deviation_lower: Optional[Decimal] = Field(
        None,
        description="The lower deviation limit in the specified unit. Use None if unspecified.",
        examples=[Decimal("-0.05")],
    )

    deviation_upper: Optional[Decimal] = Field(
        None,
        description="The upper deviation limit in the specified unit. Use None if unspecified.",
        examples=[Decimal("0.05")],
    )

    fit: Optional[str] = Field(
        None,
        description="The fit specification, such as 'H7'. Optional if not applicable.",
        examples=["H7"],
    )

    is_theoretically_exact: bool = Field(
        False,
        description="Whether the tolerance is theoretically exact (e.g., basic dimensions).",
    )

    is_reference: bool = Field(
        False,
        description="Whether the tolerance serves as a reference dimension.",
    )

    is_general_tolerance: bool = Field(
        False,
        description="Whether the general tolerance was applied to this dimension.",
    )

    is_approximation: bool = Field(
        False,
        description="Whether the tolerance is an approximation (e.g., 'approx. 5').",
    )


class Size(Quantity):
    """
    Represents a size definition for a part or feature in an engineering context.
    """

    size_type: SizeType = Field(
        ...,
        description="The type of size (e.g., diameter, linear, angular).",
        examples=[SizeType.DIAMETER],
    )

    tolerance: Optional[Tolerance] = Field(
        None,
        description="The tolerance specifications associated with the size.",
        examples=[
            Tolerance(
                fit="H7",
                deviation_lower=Decimal("-0.05"),
                deviation_upper=Decimal("0.05"),
                tolerance_grade="IT7",
            )
        ],
    )


class Depth(BaseModel):
    """
    Represents the depth of a feature, such as a hole or bore.
    """

    depth_type: DepthType
    size: Optional[Size]


class Dimension(Feature):
    """
    Represents a measurement cue in an engineering or technical drawing.
    """

    quantity: int = Field(
        ...,
        ge=0,
        description="The quantity or value associated with the measurement, must be non-negative.",
        examples=[10],
    )

    size: Size = Field(
        ...,
        description="Details about the size, including type, nominal value, tolerance, and unit.",
    )


class ThreadSpacing(BaseModel):
    """
    Represents the spacing of a thread, defining the distance between thread crests.
    """

    pitch_in_mm: Decimal = Field(
        ...,
        description="The pitch of the thread, defining the distance between thread crests.",
    )

    threads_per_inch: Decimal = Field(
        ...,
        ge=0,
        description="The number of threads per inch (TPI) for imperial threads. Must be non-negative.",
        examples=[Decimal("20")],
    )


class Thread(Feature):
    """
    Represents a generic threaded feature in an engineering or technical drawing.
    """

    quantity: Decimal = Field(
        ...,
        ge=0,
        description="The number of threads or instances. Must be non-negative.",
        examples=[Decimal("1")],
    )

    diameter: Size = Field(
        ...,
        description="The diameter of the thread, including nominal size and tolerances.",
    )

    spacing: Optional[ThreadSpacing] = Field(
        ...,
        description="The spacing of the thread, defining the distance between thread crests.",
    )

    handedness: ThreadHandedness = Field(
        ..., description="The direction of the thread, such as LEFT or RIGHT."
    )

    depth: Optional[Depth] = Field(
        default=None,
        description="The length of the threaded feature, including nominal size and tolerances.",
    )


class ThreadISOMetric(Thread):
    """
    Represents an ISO Metric thread.
    """

    thread_type: Literal[ThreadType.ISO_METRIC] = ThreadType.ISO_METRIC
    female_major_diameter_tolerance: Optional[Tolerance] = Field(
        None,
        description="Tolerance for the major diameter of female threads.",
    )
    female_pitch_diameter_tolerance: Optional[Tolerance] = Field(
        None,
        description="Tolerance for the pitch diameter of female threads.",
    )
    male_major_diameter_tolerance: Optional[Tolerance] = Field(
        None,
        description="Tolerance for the major diameter of male threads.",
    )
    male_pitch_diameter_tolerance: Optional[Tolerance] = Field(
        None, description="Tolerance for the pitch diameter of male threads."
    )


class ThreadSM(Thread):
    """
    Represents a screw machine (SM) thread.
    """

    thread_type: Literal[ThreadType.SM] = ThreadType.SM
    sm_size: Decimal = Field(..., description="The size of the SM thread.")


class ThreadUTS(Thread):
    """
    Represents a Unified Thread Standard (UTS) thread.
    """

    thread_type: Literal[ThreadType.UTS] = ThreadType.UTS
    uts_size: str = Field(
        ...,
        description="The nominal size of the UTS thread.",
        examples=["1/4", "1/2"],
    )
    uts_series: str = Field(
        ...,
        description="The series designation of the UTS thread.",
        examples=["UNC", "UNF"],
    )
    uts_tolerance_class: str = Field(
        ...,
        description="The tolerance class for the UTS thread.",
        examples=["2A", "3B"],
    )


class ThreadACME(Thread):
    """
    Represents an ACME thread.
    """

    thread_type: Literal[ThreadType.ACME] = ThreadType.ACME
    acme_size: str = Field(
        ...,
        description="The nominal size of the ACME thread.",
        examples=["1/4", "1/2"],
    )
    acme_series: str = Field(
        ...,
        description="The series designation of the ACME thread.",
        examples=["ACME", "STUB ACME"],
    )


class ThreadNPT(Thread):
    """American National Standard Pipe Thread standards,
    often called National Pipe Thread (NPT) standards.
    """

    thread_type: Literal[ThreadType.NPT] = ThreadType.NPT
    npt_size: str = Field(
        ...,
        description="The nominal size of the NPT thread.",
    )
    npt_series: str = Field(
        ...,
        description="The series designation of the NPT thread.",
        examples=["NPT", "NPS"],
    )


class ThreadWhitworth(Thread):
    """
    Represents a Whitworth thread.
    """

    thread_type: Literal[ThreadType.WHITWORTH] = ThreadType.WHITWORTH
    whitworth_size: Decimal = Field(
        ...,
        description="The nominal size of the Whitworth thread.",
    )
    whitworth_tolerance_class: Optional[str] = Field(
        None,
        description="The tolerance class for the Whitworth thread.",
    )


class ThreadKnuckle(Thread):
    """
    Represents a Knuckle thread.
    """

    thread_type: Literal[ThreadType.KNUCKLE] = ThreadType.KNUCKLE
    knuckle_size: str = Field(
        ...,
        description="The nominal size of the Knuckle thread.",
    )
    knuckle_series: str = Field(
        ...,
        description="The series designation of the Knuckle thread.",
    )
    knuckle_profile: Optional[str] = Field(
        None,
        description="The profile of the Knuckle thread.",
    )


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
    """

    quantity: int = Field(
        ...,
        ge=1,
        description="The number of chamfers or instances. Must be at least 1.",
    )

    size: Size = Field(
        ...,
        description="The linear size of the chamfer, such as the width or depth.",
        examples=[
            Size(
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
            )
        ],
    )

    angle: Size = Field(
        ...,
        description="The angle of the chamfer, typically specified in degrees.",
        examples=[
            Size(
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
            )
        ],
    )


class Counterbore(BaseModel):
    """
    Represents a counterbore feature in an engineering or technical drawing.
    """

    diameter: Size = Field(
        ...,
        description="The diameter of the counterbore.",
        examples=[
            Size(
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
            )
        ],
    )
    depth: Depth = Field(
        ...,
        description="The depth of the counterbore.",
        examples=[
            Size(
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
            )
        ],
    )


class Countersink(BaseModel):
    """
    Represents a countersink feature in an engineering or technical drawing.
    """

    diameter: Size = Field(
        ...,
        description="The diameter of the countersink.",
        examples=[
            Size(
                size_type=SizeType.DIAMETER,
                value=Decimal("15"),
                tolerance=None,
                unit="millimeter",
            )
        ],
    )
    angle: Size = Field(
        ...,
        description="The angle of the countersink, typically in degrees.",
        examples=[
            Size(
                size_type=SizeType.ANGULAR,
                value=Decimal("90"),
                tolerance=None,
                unit="degree",
            )
        ],
    )


class Counterdrill(BaseModel):
    """
    Represents a counterdrill feature in an engineering or technical drawing.
    """

    diameter: Size = Field(
        ...,
        description="The diameter of the counterdrill.",
        examples=[
            Size(
                size_type=SizeType.DIAMETER,
                value=Decimal("8"),
                tolerance=None,
                unit="millimeter",
            )
        ],
    )
    depth: Depth = Field(
        ...,
        description="The depth of the counterdrill.",
        examples=[
            Size(
                size_type=SizeType.LINEAR,
                value=Decimal("20"),
                tolerance=None,
                unit="millimeter",
            )
        ],
    )
    angle: Optional[Size] = Field(
        ...,
        description="The angle of the counterdrill, typically in degrees.",
        examples=[
            Size(
                size_type=SizeType.ANGULAR,
                value=Decimal("118"),
                tolerance=None,
                unit="degree",
            )
        ],
    )


class Bore(Feature):
    """
    Represents a bore feature in an engineering or technical drawing.
    """

    quantity: int = Field(
        ...,
        ge=1,
        description="The number of bores or instances. Must be at least 1.",
        examples=[2],
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
        examples=[
            Size(
                size_type=SizeType.DIAMETER,
                value=Decimal("10"),
                tolerance=None,
                unit="millimeter",
            )
        ],
    )
    depth: Optional[Depth] = Field(
        ...,
        description="The depth of the bore.",
        examples=[
            Depth(
                size=Size(
                    size_type=SizeType.LINEAR,
                    value=Decimal("50"),
                    tolerance=None,
                    unit="millimeter",
                ),
                depth_type=DepthType.SIZE,
            )
        ],
    )
    thread: Optional[Reference] = Field(
        None, description="Reference to the reference_id of the associated thread."
    )


class RoughnessWaviness(BaseModel):
    """
    Represents the waviness characteristics of a surface in terms of height and width.
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
    """

    length: Optional[Size]
    lambda_c_multiple: Optional[Decimal]


class RoughnessCondition(BaseModel):
    """
    Represents a condition for surface roughness specified on a technical drawing.
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
        examples=["N6"],
    )


class Roughness(Feature):
    """
    Represents the roughness specifications on a technical drawing.
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
    """

    process_category: List[str] = Field(
        ...,
        description="The category of the process based on DIN 8580, e.g., forming or coating.",
        examples=[["SEPARATION", "CUTTING", "WATERJET_CUTTING"]],
    )


class GDnTDatum(BaseModel):
    """
    Represents a GD&T datum definition.
    """

    label: str = Field(
        ...,
        description=(
            "Reference name of the datum. Examples: 'A', 'B', or composite names "
            "such as '(A-B-C-D)[CM]'."
        ),
    )


class GDnTExtend(Size):
    """
    Represents the extend of the GD&T Zone
    """

    quantity: int = Field(
        1,
        description="The number of extends",
        examples=[1],
    )
    angle: Optional[Decimal] = Field(
        None,
        description="The angle of the extend",
        examples=[Decimal("45")],
    )


class GDnTZone(BaseModel):
    """
    Representation of the GDT GD&T Value
    """

    value: Size = Field(
        ...,
        description="The value of the GD&T zone.",
    )
    extend: Optional[GDnTExtend] = Field(
        None,
        description="The extend of the GD&T zone.",
    )
    combination: Optional[str] = Field(
        None,
        description="The combination of the GD&T zone.",
    )
    offset: Optional[str] = Field(
        None,
        description="The offset of the GD&T zone.",
    )
    constraint: Optional[str] = Field(
        None,
        description="The constraint of the GD&T zone.",
    )


class GDnTFeature(BaseModel):
    """
    Represents the feature of the GD&T
    """

    filter: Optional[str] = Field(
        None,
        description="Filter for the feature",
    )
    associated_feature: Optional[GDnTAssociatedFeature] = Field(
        None,
        description="Associated feature for the GD&T",
    )
    derived_feature: Optional[GDnTDerivedFeature] = Field(
        None,
        description="Derived feature for the GD&T",
    )


class GDnTReference(BaseModel):
    """
    Represents a reference for a GD&T characteristic.
    """

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


class Geometry(BaseModel, abc.ABC):
    """
    Base class for representing geometric shapes.
    """

    geometry_type: GeometryType


class GeometryCuboid(Geometry):
    """
    Represents the geometry of a cuboid
    """

    geometry_type: Literal[GeometryType.CUBOID] = GeometryType.CUBOID

    width: Size = Field(
        ...,
        description="The width of the cuboid.",
    )
    height: Size = Field(
        ...,
        description="The height of the cuboid.",
    )
    depth: Size = Field(
        ...,
        description="The depth of the cuboid.",
    )


class GeometryCylinder(Geometry):
    """
    Represents the geometry of a plate-shaped material.
    """

    geometry_type: Literal[GeometryType.CYLINDER] = GeometryType.CYLINDER
    diameter: Size = Field(
        ...,
        description="The diameter of the cylinder.",
    )
    depth: Size = Field(
        ...,
        description="The depth of the cylinder.",
    )


class Material(BaseModel):
    """
    Represents a material definition with raw OCR text, standard name, designation, and
    """

    raw_ocr: str = Field(
        ...,
        description="Raw OCR text extracted from the drawing.",
    )
    standard: Optional[str] = Field(
        None,
        description="Standard that defines the standard.",
    )
    designation: str = Field(
        ...,
        description="Designation of the material following the spelling used in the standard.",
    )
    material_category: tuple[
        Optional[MaterialCategory1],
        Optional[MaterialCategory2],
        Optional[MaterialCategory3],
    ] = Field(
        ...,
        description="Hierarchical Material category.",
    )


class MaterialCombination(Reference):
    """
    List of Materials that need to be combined
    (Material_A and Material_B) is a material combination
    """

    material_combination: list[Material] = Field(
        ...,
        description="List of materials that need to be used together.",
    )


class BillOfMaterialRow(BaseModel):
    """
    Represents a single row in a bill of material (BOM) table.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    position: Optional[str] = Field(
        None,
        description="Position Number of the part on the assembly, defined using position bubbles.",
    )
    part_number: Optional[str] = Field(
        None,
        description="Part Number of the parts listed in the bill of material.",
    )
    designation: Optional[str] = Field(
        None,
        description="Designation/Title of the part listed in the bill of material.",
    )
    material_options: list[MaterialCombination] = Field(
        default_factory=list,
        description="List of possible MaterialCombinations",
    )
    quantity: Optional[Quantity] = Field(
        None, description="Physical quantity in the string format of Pint."
    )
    unit_weight: Optional[Quantity] = Field(
        None, description="Unit Weight of the parts listed in the bill of material."
    )


class BillOfMaterial(Reference):
    """
    Represents a bill of material (BOM) table in a technical drawing.
    """

    rows: List[BillOfMaterialRow] = Field(
        ...,
        description="List of rows in the bill of material.",
    )


class RevisionTableRow(BaseModel):
    """
    Represents a single row in a revision table, documenting changes made
    to a drawing or technical document.
    """

    revision_serial: Optional[str] = Field(
        None,
        description=(
            "Serial number used to identify the revision, typically indicated by "
            "letters (e.g., 'A', 'B') or numbers (e.g., '01', '02')."
        ),
        examples=["A"],
    )

    description: str = Field(
        ...,
        description="Description of the change or revision made.",
        examples=["Added dimension to part edge."],
    )

    revision_date: Optional[date] = Field(
        None,
        description="The date when the revision was implemented.",
        examples=["2025-01-24"],
    )


class RevisionTable(Reference):
    """
    Represents a revision table in a technical drawing, documenting changes made
    """

    rows: list[RevisionTableRow] = Field(
        ...,
        description="List of rows in the revision table.",
    )


class Note(Feature):
    """
    Represents a note in a technical drawing.
    """

    note_type: NoteType = Field(
        ...,
        description=(
            "The type of the note, specifying whether it is a canvas note, sectional note, "
            "or a sectional feature."
        ),
    )


class Radius(Feature):
    """
    Represents a radius feature in an engineering or technical drawing.
    """

    quantity: int = Field(
        ...,
        ge=0,
        description="The quantity or value associated with the measurement, must be non-negative.",
    )
    curvature_type: Optional[CurvatureType] = Field(
        None,
        description="The type of curvature for the radius, such as concave or convex. This is only set if the label explicitly states it (e.g., 'R10 concave').",
    )
    size: Size = Field(
        ...,
        description="Details about the size, including type, nominal value, tolerance, and unit.",
    )


class UnitSystem(Reference):
    """
    Represents the unit system used in the technical drawing
    """

    unit_system_type: UnitSystemType


class ProjectionMethod(Reference):
    """Projection Method according to ISO 128"""

    projection_method: ProjectionMethodType


class PrimaryProcessCutting(BaseModel):
    """
    Represents a cutting process in a technical drawing.
    """

    primary_process: Literal[PrimaryProcessType.CUTTING] = PrimaryProcessType.CUTTING
    requires_bending: Optional[bool] = Field(
        None,
        description="Whether the cutting process requires bending.",
    )


class PrimaryProcessTurning(BaseModel):
    primary_process: Literal[PrimaryProcessType.TURNING] = PrimaryProcessType.TURNING
    requires_secondary_milling: bool = Field(
        ...,
        description="Whether the turning process requires secondary milling.",
    )


class PrimaryProcessMilling(BaseModel):
    primary_process: Literal[PrimaryProcessType.MILLING] = PrimaryProcessType.MILLING
    axis_count: Optional[int] = Field(
        None,
        description="The number of axes used in the milling process.",
    )


PrimaryProcessUnion = Union[
    PrimaryProcessCutting, PrimaryProcessTurning, PrimaryProcessMilling
]


class Polygon(BaseModel):
    """
    Represents a polygon area in the drawing.
    """

    coordinate_space: CoordinateSpace = Field(
        ...,
        description="The coordinate space used to define the polygon, such as absolute or relative.",
    )
    coordinates: list[tuple[int, int]] = Field(
        ...,
        description="A list of x,y tuples representing the vertices of the polygon.",
    )


class VolumeEstimate(Quantity):
    """
    Represents a volume estimate for a part or feature.
    """

    volume_estimate_type: VolumeEstimateType = Field(
        ...,
        description="The type of volume estimate, such as gross or net volume.",
    )


class ReferencePosition(BaseModel):
    """
    Represents the position of a reference in the drawing.
    """

    reference_id: int = Field(
        ...,
        description="Reference ID to identify the object.",
        examples=[12345],
    )
    polygon: Optional[Polygon]


class RedactionKeyword(BaseModel):
    """
    A class that represents a keyword to redact from the drawing.
    """

    keyword: str = Field(..., description="The keyword to redact from the drawing.")


class RedactionZone(BaseModel):
    """
    A class that represents a redacted area in the drawing.
    """

    redaction_zone_type: RedactionZoneType
    polygon: Polygon = Field(
        ...,
        description="A list of x,y tuples representing the vertices of the redacted area.",
    )


class BoundingDimensions(BaseModel):
    """
    Represents the bounding dimensions of a component.
    """

    enclosing_cuboid: Optional[GeometryCuboid] = Field(
        None,
        description="The enclosing cuboid of the component.",
    )
    enclosing_cylinder: Optional[GeometryCylinder] = Field(
        None,
        description="The enclosing cylinder of the component.",
    )
