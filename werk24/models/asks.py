from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field

from .enums import PageType, RedactionZoneType
from .models import (
    BillOfMaterial,
    Bore,
    CalloutPosition,
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
    Roughness,
    SecondaryProcess,
    ThreadUnion,
    UnitSystem,
    VolumeEstimate,
    Weight,
)
from .v1.ask import W24Ask


class AskType(str, Enum):
    """The type of request to be sent to the server."""

    CALLOUT_POSITIONS = "CALLOUT_POSITIONS"
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


class AskCalloutPositions(AskV2):
    """Represents a request for the position of a component in the drawing."""

    ask_type: Literal[AskType.CALLOUT_POSITIONS] = AskType.CALLOUT_POSITIONS


class Answer(BaseModel):
    """
    A class that represents an answer to a request from the server.

    """

    ask_version: Literal["v2"] = "v2"


class AnswerCalloutPositions(Answer):
    """
    A class that represents an answer to a request for the position of a component in the drawing.

    Attributes:
    ----------
    - callout_positions (List[CalloutPosition]): The positions of the component in the drawing.
    """

    ask_type: Literal[AskType.CALLOUT_POSITIONS] = AskType.CALLOUT_POSITIONS

    callout_positions: list[CalloutPosition] = Field(
        ..., description="The positions of the component in the drawing."
    )


class AskMetaData(AskV2):
    """A class that represents a request for metadata
    from the server.
    """

    ask_type: Literal[AskType.META_DATA] = AskType.META_DATA


class AnswerMetaData(Answer):
    ask_type: Literal[AskType.META_DATA] = AskType.META_DATA


class AnswerMetaDataMiscellaneous(AnswerMetaData):
    """
    A class that represents an answer to for a page that is NOT a component drawing.
    """

    page_type: Literal[PageType.MISCELLANEOUS] = PageType.MISCELLANEOUS


class AnswerMetaDataMechanicalComponent(AnswerMetaData):
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


class AnswerInsights(Answer):
    ask_type: Literal[AskType.INSIGHTS] = AskType.INSIGHTS


class AnswerInsightsMechanicalComponent(AnswerInsights):
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


class AskFeatures(AskV2):
    """A class that represents a request for vallouts
    from the server.
    """

    ask_type: Literal[AskType.FEATURES] = AskType.FEATURES


class AnswerFeatures(Answer):
    ask_type: Literal[AskType.FEATURES] = AskType.FEATURES


class AnswerFeaturesMiscallaneous(Answer):
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


ASK_SUBCLASSES = {cls.__name__: cls for cls in get_ask_subclasses()}
AskUnion = Union[tuple(ASK_SUBCLASSES.values())]
