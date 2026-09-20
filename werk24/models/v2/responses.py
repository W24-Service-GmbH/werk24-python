import abc
from typing import Any, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from .enums import AskType, PageType, PaperSize
from .models import (
    Balloon,
    BillOfMaterial,
    Bore,
    BoundingDimensions,
    Certification,
    Chamfer,
    Dimension,
    Entry,
    GDnT,
    GeneralTolerances,
    Identifier,
    Language,
    MaterialCombination,
    Note,
    PageAssessment,
    PrimaryProcessUnion,
    ProcessingTimeEstimate,
    ProjectionMethod,
    Radius,
    RedactionZone,
    ReferencePosition,
    Roughness,
    SecondaryProcess,
    ThreadUnion,
    UnitSystem,
    VolumeEstimate,
    Weight,
)


class Response(BaseModel, abc.ABC):
    """
    A class that represents an Response to a request from the server.

    """

    ask_version: Literal["v2"] = "v2"


class ResponseBalloons(Response):
    """
    `ResponseBalloons` is the corresponding response object for `AskBalloons`.
    It contains the extracted balloon details from the technical drawing.

    """

    ask_type: Literal[AskType.BALLOONS] = AskType.BALLOONS
    balloons: List[Balloon] = Field(
        ..., description="The balloons in the technical drawing."
    )


class ResponseCustom(Response):
    ask_type: Literal[AskType.CUSTOM] = AskType.CUSTOM
    custom_id: str = Field(..., description="The ID of the custom output.")
    output: Any = Field(..., description="The custom output.")


class ResponseDocumentProfile(Response):
    """
    The document's shape: how big it is, and how long it is likely to take.

    Read off the file itself, before any interpretation begins and without
    asking a model anything, so it arrives in milliseconds rather than
    seconds. Use it to tell a waiting user how long they are waiting.

    **What kind of page this is is no longer here.** It costs a vision call,
    which is thousands of times slower than everything in this response, so
    keeping the two together meant the fast answer waited for the slow one.
    Ask `AskPageAssessment` for it, and for whether the pages carry welding.
    """

    ask_type: Literal[AskType.DOCUMENT_PROFILE] = AskType.DOCUMENT_PROFILE

    page_count: int = Field(
        ...,
        ge=1,
        description=(
            "Number of pages in the document, before any page limit is "
            "applied. Note that this does NOT drive the processing-time "
            "estimate: measured over 4,639 requests, two-page documents come "
            "back faster than one-page ones, so the estimate is keyed on "
            "sheet size instead."
        ),
        examples=[1, 12],
    )
    paper_size: Optional[PaperSize] = Field(
        None,
        description=(
            "The sheet format. CUSTOM for a real sheet that is not one of the "
            "named formats. None for inputs that state no physical size, "
            "which is every raster image: a photograph or a scan carries "
            "pixels, not millimetres."
        ),
        examples=[PaperSize.A3, PaperSize.ANSI_D, PaperSize.CUSTOM],
    )
    processing_time: Optional[ProcessingTimeEstimate] = Field(
        None,
        description=(
            "How long this document is likely to take. None when the shape is "
            "too unusual to compare against anything we have measured; treat "
            "that as 'no estimate' rather than 'fast'."
        ),
    )


class ResponsePageAssessment(Response):
    """
    What each page of the document is, and whether it shows welding.

    One entry per page **we were asked to read**, in the order we read them,
    which is not necessarily the order they appear in the file: a request that
    names particular pages gets those pages, and a page limit truncates the
    rest. `ResponseDocumentProfile.page_count` reports the length of the whole
    document, so the two legitimately disagree.

    A `None` entry means that page could not be assessed, which is not the
    same as a page assessed as ordinary. Do not read it as "no welding".

    This response waits on a model, so it arrives well after
    `ResponseDocumentProfile` and roughly alongside the extraction results.
    """

    ask_type: Literal[AskType.PAGE_ASSESSMENT] = AskType.PAGE_ASSESSMENT

    pages: List[Optional[PageAssessment]] = Field(
        default_factory=list,
        description=(
            "One entry per page read, in reading order. None where the page "
            "could not be assessed at all, which is distinct from a page "
            "assessed as MISCELLANEOUS with no welding."
        ),
    )


class ResponseFeaturesComponentDrawing(Response):
    """
    Represents an Response to a request for features of a mechanical component drawing from the server.
    It contains extracted features from the technical drawing, providing structured data for further processing.
    """

    ask_type: Literal[AskType.FEATURES] = AskType.FEATURES
    page_type: Literal[PageType.COMPONENT_DRAWING] = PageType.COMPONENT_DRAWING

    bores: List[Bore] = Field(
        default_factory=list,
        description="Bore specifications for the component (e.g., `Ø6 H7 (+0.012/0) ↧13.4`, `6x Ø3.3 ↧12.0 ⌵ Ø3.3x45° M4×0.7—6H/6g×8.0`).",
    )
    chamfers: List[Chamfer] = Field(
        default_factory=list,
        description="Chamfer specifications for the component (e.g., `3 x 45°`, `4x 0.031 x 45.00° TYPICAL`).",
    )
    dimensions: List[Dimension] = Field(
        default_factory=list,
        description="Dimension details for the component (e.g, `5 ±0.3`, `Ø30`, `□5`). ",
    )
    gdnts: List[GDnT] = Field(
        default_factory=list,
        description="Geometric dimensioning and tolerancing (GD&T) details (e.g., `[◎|Ø0.02|A-B]`).",
    )
    radii: List[Radius] = Field(
        default_factory=list,
        description="Radius specifications for the component (e.g., `R5`).",
    )
    roughnesses: List[Roughness] = Field(
        default_factory=list,
        description="Additional surface roughness details beyond general roughness. (e.g., `√URa  12.5`)",
    )
    threads: List[ThreadUnion] = Field(
        default_factory=list,
        description="Thread specifications for the component (e.g., `M5×0.8—6g/6H`, `0.25—20 UNC—2A`).",
    )


class ResponseInsightsComponentDrawing(Response):
    """
    `ResponseInsightsComponentDrawing` is the response object corresponding to an AskInsights request.
    It provides structured insights into the manufacturability and processing of a mechanical component.
    """

    ask_type: Literal[AskType.INSIGHTS] = AskType.INSIGHTS
    page_type: Literal[PageType.COMPONENT_DRAWING] = PageType.COMPONENT_DRAWING

    dimensions_before_processing: Optional[BoundingDimensions] = Field(
        None,
        description="The bounding dimensions of the component before processing.",
    )

    dimensions_after_processing: Optional[BoundingDimensions] = Field(
        None,
        description="The bounding dimensions of the component after processing.",
    )

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


class ResponseMetaDataComponentDrawing(Response):
    """
    `ResponseMetaData` represents the structured response to a metadata request (AskMetaData)
    for a mechanical component drawing. This response provides essential details such as identifiers,
    material options, unit systems, general tolerances, and other metadata extracted from the drawing.

    The response enables better integration with manufacturing systems,
    PLM (Product Lifecycle Management), and ERP systems by providing structured component details.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    ask_type: Literal[AskType.META_DATA] = AskType.META_DATA
    page_type: Literal[PageType.COMPONENT_DRAWING] = PageType.COMPONENT_DRAWING

    bill_of_material: Optional[BillOfMaterial] = Field(
        None,
        description="Bill of materials for the component, listing parts and quantities.",
    )
    certifications: List[Certification] = Field(
        default_factory=list,
        description="List of certifications associated with the component.",
    )
    designation: list[Entry] = Field(
        default_factory=list,
        description="Designation of the component.",
    )
    identifiers: List[Identifier] = Field(
        default_factory=list,
        description="List of identifiers associated with the component.",
    )
    general_roughness: Optional[Roughness] = Field(
        None,
        description="General roughness specifications for the component.",
    )
    general_tolerances: Optional[GeneralTolerances] = Field(
        None,
        description="General tolerance specifications for the component.",
    )
    languages: List[Language] = Field(
        default_factory=list,
        description="Languages used in the drawing.",
    )
    material_options: List[MaterialCombination] = Field(
        default_factory=list,
        description="Material options available for the component.",
    )
    notes: list[Note] = Field(
        default_factory=list,
        description="List of all notes in the drawing.",
    )
    projection_method: Optional[ProjectionMethod] = Field(
        None,
        description="Projection method used in the drawing (e.g., first angle or third angle).",
    )
    unit_systems: List[UnitSystem] = Field(
        default_factory=list,
        description="The units specification for the component.",
    )
    weight: Optional[Weight] = Field(
        None,
        description="Weight of the component.",
    )


class ResponseRedaction(Response):
    """
    A class that represents an Response to a redaction request from the server.
    """

    ask_type: Literal[AskType.REDACTION] = AskType.REDACTION

    redaction_zones: list[RedactionZone] = Field(
        default_factory=list, description="A list of redacted areas in the drawing."
    )


class ResponseReferencePositions(Response):
    """
    A class that represents an Response to a request for the position of a component in the drawing.
    """

    ask_type: Literal[AskType.REFERENCE_POSITIONS] = AskType.REFERENCE_POSITIONS

    reference_positions: list[ReferencePosition] = Field(
        ..., description="The positions of the component in the drawing."
    )


def get_response_subclasses() -> List:
    subclasses = Response.__subclasses__()
    # Recursively collect subclasses of subclasses, if any
    for subclass in subclasses:
        subclasses.extend(subclass.__subclasses__())
    return subclasses


RESPONSE_SUBCLASSES = get_response_subclasses()
ResponseUnion = Union[tuple(RESPONSE_SUBCLASSES)]
