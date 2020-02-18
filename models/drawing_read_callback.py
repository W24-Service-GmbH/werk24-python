from typing import Optional, List
from pydantic import BaseModel
from .measure import W24Measure
from .attachment import W24Attachment


class W24IoCallbackResponse(BaseModel):
    callback_secret: str
    thumbnail_page: Optional[W24Attachment] = None
    thumbnail_sheet: Optional[W24Attachment] = None
    thumbnail_canvas: Optional[W24Attachment] = None
    measures: Optional[List[W24Measure]] = None
