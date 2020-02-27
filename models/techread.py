from enum import Enum
from typing import List, Optional, Union

from pydantic import UUID4, BaseModel, HttpUrl, Json

from .architecture import W24Architecture
from .ask_measures import W24AskMeasures
from .ask_thumbnail_canvas import W24AskThumbnailCanvas
from .ask_thumbnail_page import W24AskThumbnailPage
from .ask_thumbnail_sheet import W24AskThumbnailSheet


class W24TechreadCommand(BaseModel):
    action: str
    message: Json


class W24TechreadMessageType(str, Enum):
    TECHREAD_INITIALIZATION_SUCCESS = "TECHREAD_INITIALIZATION_SUCCESS"
    TECHREAD_STARTED = "TECHREAD_STARTED"


class W24TechreadMessage(BaseModel):
    request_id: Optional[UUID4]
    message_type: W24TechreadMessageType
    payload_json: Optional[Json]
    payload_url: Optional[HttpUrl]


class W24TechreadRequest(BaseModel):
    """ Definition of a W24DrawingReadRequest describing
    (i) the Technical Drawing,
    (ii) the associated 3D-Model (optional),
    (iii) the list of features that shall be extracted,
    (iv) the architecture on which to run the algorithm
    (v) the callback url that shall be called after the
    """

    asks: List[Union[
        W24AskMeasures,
        W24AskThumbnailCanvas,
        W24AskThumbnailPage,
        W24AskThumbnailSheet]] = []
    architecture: W24Architecture
