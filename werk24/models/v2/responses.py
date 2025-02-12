import abc
from typing import Any, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from .enums import AskType, PageType
from .models import (
    Balloon,
    BillOfMaterial,
    Bore,
    Chamfer,
    Dimension,
    Entry,
    GDnT,
    GeneralTolerances,
    GeometryCuboid,
    GeometryCylinder,
    Identifier,
    Language,
    MaterialCombination,
    PrimaryProcessUnion,
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
    ask_type: Literal[AskType.BALLOONS] = AskType.BALLOONS
    balloons: List[Balloon] = Field(
        ..., description="The balloons in the technical drawing."
    )


class ResponseCustom(Response):
    ask_type: Literal[AskType.CUSTOM] = AskType.CUSTOM
    custom_id: str = Field(..., description="The ID of the custom output.")
    output: Any = Field(..., description="The custom output.")


class ResponseFeaturesComponentDrawing(Response):
    """
    Represents an Response to a request for features of a mechanical component drawing from the server.
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


class ExternalDimensions(BaseModel):
    """
    Represents the external dimensions of a component.
    """

    enclosing_cuboid: Optional[GeometryCuboid] = Field(
        None,
        description="The enclosing cuboid of the component.",
    )
    enclosing_cylinder: Optional[GeometryCylinder] = Field(
        None,
        description="The enclosing cylinder of the component.",
    )


class ResponseInsightsComponentDrawing(Response):
    ask_type: Literal[AskType.INSIGHTS] = AskType.INSIGHTS
    page_type: Literal[PageType.COMPONENT_DRAWING] = PageType.COMPONENT_DRAWING

    dimensions_before_processing: Optional[ExternalDimensions] = Field(
        None,
        description="The external dimensions of the component before processing.",
    )

    dimensions_after_processing: Optional[ExternalDimensions] = Field(
        None,
        description="The external dimensions of the component after processing.",
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
    """A class that represents an Response to a request for metadata of a mechanical component drawing from the server."""

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
    unit_systems: List[UnitSystem] = Field(
        default_factory=list,
        description="The units specification for the component.",
    )


class ResponseRedaction(Response):
    """
    A class that represents an Response to a redaction request from the server.
    """

    ask_type: Literal[AskType.REDACTION] = AskType.REDACTION

    redaction_zones: list[RedactionZone] = Field(
        ..., description="A list of redacted areas in the drawing."
    )


class ResponseReferencePositions(Response):
    """
    A class that represents an Response to a request for the position of a component in the drawing.
    """

    ask_type: Literal[AskType.REFERENCE_POSITIONS] = AskType.REFERENCE_POSITIONS

    reference_positions: list[ReferencePosition] = Field(
        ..., description="The positions of the component in the drawing."
    )


def get_Response_subclasses() -> List:
    subclasses = Response.__subclasses__()
    # Recursively collect subclasses of subclasses, if any
    for subclass in subclasses:
        subclasses.extend(subclass.__subclasses__())
    return subclasses


RESPONSE_SUBCLASSES = get_Response_subclasses()
ResponseUnion = Union[tuple(RESPONSE_SUBCLASSES)]
