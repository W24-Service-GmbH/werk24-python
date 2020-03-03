from enum import Enum
from typing import List, Optional, Union, Dict

from pydantic import UUID4, BaseModel, HttpUrl, Json

from .architecture import W24Architecture
from .ask import W24AskThumbnailPage, W24AskThumbnailSheet, W24AskThumbnailDrawing, W24AskPartOuterDimensions


class W24TechreadCommand(BaseModel):
    action: str
    message: Json


class W24TechreadMessageType(str, Enum):
    ASK_THUMBNAIL_PAGE = "ASK_THUMBNAIL_PAGE"
    ASK_THUMBNAIL_SHEET = "ASK_THUMBNAIL_SHEET"
    ASK_THUMBNAIL_DRAWING = "ASK_THUMBNAIL_DRAWING"
    ASK_PART_OUTER_DIMENSIONS = "ASK_PART_OUTER_DIMENSIONS"
    TECHREAD_INITIALIZATION_SUCCESS = "TECHREAD_INITIALIZATION_SUCCESS"
    TECHREAD_COMPLETED = "TECHREAD_COMPLETED"
    TECHREAD_STARTED = "TECHREAD_STARTED"


class W24TechreadMessage(BaseModel):
    request_id: Optional[UUID4]
    message_type: W24TechreadMessageType
    payload_dict: Optional[Dict] = None
    payload_url: Optional[HttpUrl] = None
    payload_bytes: Optional[bytes]


class W24TechreadRequest(BaseModel):
    """ Definition of a W24DrawingReadRequest describing
    (i) the Technical Drawing,
    (ii) the associated 3D-Model (optional),
    (iii) the list of features that shall be extracted,
    (iv) the architecture on which to run the algorithm
    (v) the callback url that shall be called after the
    """

    asks: List[Union[
        W24AskThumbnailPage,
        W24AskThumbnailSheet,
        W24AskThumbnailDrawing,
        W24AskPartOuterDimensions
    ]] = []
    architecture: W24Architecture
