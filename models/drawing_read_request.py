from typing import List, Optional, Union

from pydantic import BaseModel, HttpUrl
import bson
from .attachment_drawing import W24AttachmentDrawing
from .attachment_model import W24AttachmentModel
from .architecture import W24Architecture
from .ask_measures import W24AskMeasures
from .ask_thumbnail_canvas import W24AskThumbnailCanvas
from .ask_thumbnail_page import W24AskThumbnailPage
from .ask_thumbnail_sheet import W24AskThumbnailSheet
import base64


class W24DrawingReadRequest(BaseModel):
    """ Definition of a W24DrawingReadRequest describing
    (i) the Technical Drawing,
    (ii) the associated 3D-Model (optional),
    (iii) the list of features that shall be extracted,
    (iv) the architecture on which to run the algorithm
    (v) the callback url that shall be called after the
    """
    class Config:
        json_encoders = {
            bytes: lambda v: base64.b64encode(v).decode()
        }

    drawing: W24AttachmentDrawing
    model: Optional[W24AttachmentModel] = None
    asks: List[Union[
        W24AskMeasures,
        W24AskThumbnailCanvas,
        W24AskThumbnailPage,
        W24AskThumbnailSheet]] = []
    architecture: W24Architecture

    def dumps(self):
        return bson.encode(self.dict())
