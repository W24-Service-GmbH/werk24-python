from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from werk24._version import __version__

from .enums import PageType, ProjectionMethod, ThumbnailType
from .models import (
    BillOfMaterial,
    Bore,
    Chamfer,
    Dimension,
    Doubt,
    Entry,
    GDnT,
    GeneralTolerances,
    Geometry,
    Identifier,
    Language,
    MaterialCombination,
    Note,
    Process,
    Quantity,
    Radius,
    RevisionTable,
    Roughness,
    Thread,
)
from .v1.ask import W24Ask


class AskType(str, Enum):
    """The type of request to be sent to the server."""

    META_DATA = "META_DATA"
    FEATURES = "FEATURES"
    INSIGHTS = "INSIGHTS"
    THUMBNAIL = "THUMBNAIL"
    REDACTION = "REDACTION"
    CUSTOM = "CUSTOM"


class AskV2(BaseModel):
    """A class that represents a request for information
    from the server.
    """

    version: Literal["v2"] = "v2"


Ask = Union[W24Ask, "AskV2"]


class AskResponse(BaseModel):
    """
    A class that represents a response to a request from the server.

    """

    version: Literal["v2"] = "v2"
    page: int = Field(
        ..., description="The page number of the response starting from 1."
    )


class AskMetaData(AskV2):
    """A class that represents a request for metadata
    from the server.
    """

    ask_type: Literal[AskType.META_DATA] = AskType.META_DATA


class AskMetaDataResponse(AskResponse):
    ask_type: Literal[AskType.META_DATA] = AskType.META_DATA


class AskMetaDataResponseMiscellaneous(AskResponse):
    """
    A class that represents a response to for a page that is NOT a component drawing.
    """

    page_type: Literal[PageType.MISCELLANEOUS] = PageType.MISCELLANEOUS


class AskMetaDataResponseMechanicalComponent(AskResponse):
    """A class that represents a response to a request for metadata of a mechanical component drawing from the server.

    Attributes:
    ----------
    - identifiers (List[Identifier]): A list of identifiers associated with the component.
    - designation (Entry|None): Designation of the component.
    - languages (List[Language]): The languages used in the drawing.
    - general_tolerances (GeneralTolerances): General tolerance specifications.
    - general_roughness (Roughness): General roughness specifications.
    - material_options (List[MaterialCombination]): Material options for the component.
    - weight (Quantity): The weight of the component.
    - bill_of_material (List[BillOfMaterialRow]): Bill of materials for the component.
    - revision_table (List[RevisionTableRow]): Revision history of the drawing.
    - notes (List[Note]): Notes associated with the component or drawing.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    page_type: Literal[PageType.COMPONENT_DRAWING] = PageType.COMPONENT_DRAWING

    identifiers: List[Identifier] = Field(
        default_factory=list,
        description="List of identifiers associated with the component.",
    )
    designation: Entry | None = Field(
        None,
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
    weight: Optional[Quantity] = Field(
        None,
        description="Weight of the component.",
    )
    projection_method: Optional[ProjectionMethod] = Field(
        None,
        description="Projection method used in the drawing (e.g., first angle or third angle).",
    )
    revision_table: Optional[RevisionTable] = Field(
        None,
        description="Revision history of the drawing.",
    )
    bill_of_material: Optional[BillOfMaterial] = Field(
        None,
        description="Bill of materials for the component, listing parts and quantities.",
    )
    notes: List[Note] = Field(
        default_factory=list,
        description="Notes associated with the drawing or component.",
    )


class AskInsightsResponse(AskResponse):
    input_geometry: Optional[Geometry] = Field(
        ...,
        description="The input geometry or shape of the material prior to processing.",
    )

    output_geometry: Optional[Geometry] = Field(
        ...,
        description="The final geometry or shape of the material after processing.",
    )

    processes: List[Process] = Field(
        default_factory=list,
        description="List of manufacturing processes applied to the component.",
    )


class AskFeatures(AskV2):
    """A class that represents a request for features
    from the server.
    """

    ask_type: Literal[AskType.FEATURES] = AskType.FEATURES


class AskFeaturesResponse(AskResponse):
    ask_type: Literal[AskType.FEATURES] = AskType.FEATURES


class AskFeatureResponseMiscallaneous(AskResponse):
    page_type: Literal[PageType.MISCELLANEOUS] = PageType.MISCELLANEOUS


class AskFeaturesResponseMechanicalComponent(AskResponse):
    """
    Represents a response to a request for features of a mechanical component drawing from the server.

    Attributes:
    ----------
    - dimensions (List[Dimension]): Dimension details for the component.
    - threads (List[Thread]): Thread specifications for the component.
    - bores (List[Bore]): Bore specifications for the component.
    - chamfers (List[Chamfer]): Chamfer specifications for the component.
    - roughnesses (List[Roughness]): Additional surface roughness details beyond general roughness.
    - gdnts (List[GDnT]): Geometric dimensioning and tolerancing (GD&T) details.
    - radii (List[Radius]): Radius specifications for the component.
    - doubts (List[Doubt]): Doubts or ambiguities identified by the system.
    """

    page_type: Literal[PageType.COMPONENT_DRAWING] = PageType.COMPONENT_DRAWING

    dimensions: List[Dimension] = Field(
        default_factory=list,
        description="Dimension details for the component.",
    )
    threads: List[Thread] = Field(
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
    doubts: List[Doubt] = Field(
        default_factory=list,
        description="Doubts or ambiguities identified by the system.",
    )


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


class AskRedaction(AskV2):
    """
    A class that represents a request for redaction from the server.
    """

    ask_type: Literal[AskType.REDACTION] = AskType.REDACTION
    redact_individual_names: bool = Field(
        True, description="Redact the names of Individuals"
    )
    readct_company_names: bool = Field(True, description="Redact the company names")
    redact_cage_code: bool = Field(True, description="Redact the CAGE codes")
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

    polygon: list[tuple[int, int]] = Field(
        ...,
        description="A list of x,y tuples representing the vertices of the redacted area.",
    )


class AskRedactionResponse(AskResponse):
    """
    A class that represents a response to a redaction request from the server.

    Attributes:
    ----------
    - redaction_zones (HttpUrl): A list of redacted areas in the drawing.
    """

    ask_type: Literal[AskType.REDACTION] = AskType.REDACTION

    redaction_zones: list[RedactionZone] = Field(
        ..., description="A list of redacted areas in the drawing."
    )


class AskThumbnail(AskV2):
    """A class that represents a request for thumbnails
    from the server.
    """

    ask_type: Literal[AskType.THUMBNAIL] = AskType.THUMBNAIL
    thumbnail_type: ThumbnailType


def get_ask_subclasses() -> List:
    subclasses = AskV2.__subclasses__() + W24Ask.__subclasses__()
    # Recursively collect subclasses of subclasses, if any
    for subclass in subclasses:
        subclasses.extend(subclass.__subclasses__())
    return subclasses


ASK_SUBCLASSES = {cls.__name__: cls for cls in get_ask_subclasses()}
AskUnion = Union[tuple(ASK_SUBCLASSES.values())]
