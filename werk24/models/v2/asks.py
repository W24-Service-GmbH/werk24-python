import abc
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field

from werk24.models.v1.ask import W24Ask
from werk24.models.v2.enums import AskType, PostprocessorSlot, ThumbnailFileFormat
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
    - postprocessor_slot (Optional[PostprocessorSlot]): The post-processing system to
      use for this request.
    """

    ask_type: Literal[AskType.CUSTOM] = AskType.CUSTOM
    custom_id: str = Field(..., description="The ID of the custom output to request.")
    config: Dict[str, Any] = Field(
        {}, description="Configuration options for the custom output."
    )
    postprocessor_slot: Optional[PostprocessorSlot] = Field(
        None, description="Select which postprocessing system to use."
    )


class AskDocumentProfile(AskV2):
    """Represents a request for the document's profile.

    What kind of document it is, and how long it is likely to take. Answered
    from the file's shape before any interpretation begins, so it arrives
    almost immediately and costs nothing extra: use it to decide whether to
    keep waiting, what to show a user, and whether the document is one Werk24
    interprets at all.
    """

    ask_type: Literal[AskType.DOCUMENT_PROFILE] = AskType.DOCUMENT_PROFILE


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


def _names_its_own_ask_type(subclass: type) -> bool:
    """Whether *subclass* is a concrete ask rather than a shared base.

    A concrete ask declares its own ``ask_type`` as a default. A base does
    not: ``W24AskThumbnail`` carries the thumbnail fields but inherits
    ``ask_type`` from ``W24Ask``, where it is required and accepts ANY member
    of ``W24AskType``.

    That is what made it dangerous in the union. ``AskUnion`` is not
    discriminated, so pydantic tries its members in order and takes the first
    that validates. ``W24AskThumbnail`` sits ahead of most v1 asks and matches
    every one of them -- any ask type is acceptable, and its own two fields
    have defaults -- so a bare ``{"version": "v1", "ask_type": "NOTES"}``
    became a ``W24AskThumbnail`` carrying a fabricated ``file_format: JPEG``
    and ``balloons: []``, and 17 of the 28 v1 asks could not survive a
    round-trip as themselves. Keeping bases out, and pinning every concrete
    ``ask_type`` to a ``Literal``, leaves exactly one member that can match
    any given ask.
    """
    field = subclass.model_fields.get("ask_type")
    return field is not None and not field.is_required()


def get_ask_subclasses() -> List:
    """Collect every concrete ask class, v2 first and then v1."""
    subclasses = AskV2.__subclasses__() + W24Ask.__subclasses__()
    # Recursively collect subclasses of subclasses, if any
    for subclass in subclasses:
        subclasses.extend(subclass.__subclasses__())

    # Bases are traversed for their subclasses but never offered to the union
    # themselves. Deduplicated because a class reachable by more than one path
    # would otherwise appear twice.
    concrete, seen = [], set()
    for subclass in subclasses:
        if subclass in seen or not _names_its_own_ask_type(subclass):
            continue
        seen.add(subclass)
        concrete.append(subclass)
    return concrete


AskUnion = Union[tuple(get_ask_subclasses())]
