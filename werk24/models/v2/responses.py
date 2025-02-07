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


class Reponse(BaseModel, abc.ABC):
    """
    A class that represents an Reponse to a request from the server.

    """

    ask_version: Literal["v2"] = "v2"


class ReponseBalloons(Reponse):
    ask_type: Literal[AskType.BALLOONS] = AskType.BALLOONS
    balloons: List[Balloon] = Field(
        ..., description="The balloons in the technical drawing."
    )


class ReponseCustom(Reponse):
    ask_type: Literal[AskType.CUSTOM] = AskType.CUSTOM
    custom_id: str = Field(..., description="The ID of the custom output.")
    output: Any = Field(..., description="The custom output.")


class ReponseFeaturesMechanicalComponent(Reponse):
    """
    Represents an Reponse to a request for features of a mechanical component drawing from the server.

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


class ReponseInsightsMechanicalComponent(Reponse):
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


class ReponseMetaDataMechanicalComponent(Reponse):
    """A class that represents an Reponse to a request for metadata of a mechanical component drawing from the server.

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


class ReponseRedaction(Reponse):
    """
    A class that represents an Reponse to a redaction request from the server.

    Attributes:
    ----------
    - redaction_zones (HttpUrl): A list of redacted areas in the drawing.
    """

    ask_type: Literal[AskType.REDACTION] = AskType.REDACTION

    redaction_zones: list[RedactionZone] = Field(
        ..., description="A list of redacted areas in the drawing."
    )


class ReponseReferencePositions(Reponse):
    """
    A class that represents an Reponse to a request for the position of a component in the drawing.

    Attributes:
    ----------
    - reference_positions (List[ReferencePosition]): The positions of the component in the drawing.
    """

    ask_type: Literal[AskType.REFERENCE_POSITIONS] = AskType.REFERENCE_POSITIONS

    reference_positions: list[ReferencePosition] = Field(
        ..., description="The positions of the component in the drawing."
    )


def get_Reponse_subclasses() -> List:
    subclasses = Reponse.__subclasses__()
    # Recursively collect subclasses of subclasses, if any
    for subclass in subclasses:
        subclasses.extend(subclass.__subclasses__())
    return subclasses


RESPONSE_SUBCLASSES = get_Reponse_subclasses()
ReponseUnion = Union[tuple(RESPONSE_SUBCLASSES)]
