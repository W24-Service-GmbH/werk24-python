import abc
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field

from werk24.models.v1.ask import W24Ask
from werk24.models.v2.enums import AskType, ThumbnailFileFormat
from werk24.models.v2.models import RedactionKeyword


class AskV2(BaseModel, abc.ABC):
    """A class that represents a request for information
    from the server.
    """

    ask_version: Literal["v2"] = "v2"


Ask = Union[W24Ask, "AskV2"]


class AskBalloons(AskV2):
    """Represents a request for ballooning of a technical drawing."""

    ask_type: Literal[AskType.BALLOONS] = AskType.BALLOONS


class AskCustom(AskV2):
    """Represents a request for a custom output from the server.

    Attributes:
    ----------
    - custom_id (str): The ID of the custom output to request.
    - config (Dict[str, Any]): Configuration options for the custom output.
    """

    ask_type: Literal[AskType.CUSTOM] = AskType.CUSTOM
    custom_id: str = Field(..., description="The ID of the custom output to request.")
    config: Dict[str, Any] = Field(
        {}, description="Configuration options for the custom output."
    )


class AskFeatures(AskV2):
    """A class that represents a request for vallouts
    from the server.
    """

    ask_type: Literal[AskType.FEATURES] = AskType.FEATURES


class AskInsights(AskV2):
    """A class that represents a request for insights
    from the server.
    """

    ask_type: Literal[AskType.INSIGHTS] = AskType.INSIGHTS


class AskMetaData(AskV2):
    """A class that represents a request for metadata
    from the server.
    """

    ask_type: Literal[AskType.META_DATA] = AskType.META_DATA


class AskRedaction(AskV2):
    """
    A class that represents a request for redaction from the server.
    """

    ask_type: Literal[AskType.REDACTION] = AskType.REDACTION
    redact_logos: bool = Field(
        True, description="Whether to redact logos from the drawing."
    )
    redact_company_data: bool = Field(
        True, description="Whether to redact company data."
    )
    redact_personal_data: bool = Field(
        True, description="Whether to redact personal data."
    )
    redact_keywords: list[RedactionKeyword] = Field(
        [],
        description="A list of keywords to redact from the drawing. Keywords are specified as strings.",
    )
    output_format: ThumbnailFileFormat = Field(
        ThumbnailFileFormat.PDF,
        description="The desired output format for the redacted drawing",
    )
    fill_color: Optional[str] = Field(
        "#ffffff",
        description="The fill color for the redacted areas. If None, only the polygon outlines for redacted areas are returned, and the user can perform the redaction themselves.",
    )


class AskReferencePositions(AskV2):
    """Represents a request for the position of a component in the drawing."""

    ask_type: Literal[AskType.REFERENCE_POSITIONS] = AskType.REFERENCE_POSITIONS


class AskSheetImages(AskV2):
    """Represents a request for a sheet image from the server."""

    ask_type: Literal[AskType.SHEET_IMAGES] = AskType.SHEET_IMAGES


class AskViewImages(AskV2):
    """Represents a request for a view image from the server."""

    ask_type: Literal[AskType.VIEW_IMAGES] = AskType.VIEW_IMAGES


def get_ask_subclasses() -> List:
    subclasses = AskV2.__subclasses__() + W24Ask.__subclasses__()
    # Recursively collect subclasses of subclasses, if any
    for subclass in subclasses:
        subclasses.extend(subclass.__subclasses__())
    return subclasses


AskUnion = Union[tuple(get_ask_subclasses())]
