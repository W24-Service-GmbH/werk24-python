from enum import Enum
from pydantic import BaseModel


class W24PayloadType(str, Enum):
    READ_DRAWING_INITIATED = "READ_DRAWING_INITIATED"


class W24Payload(BaseModel):
    payload_type: W24PayloadType


class W24PayloadDrawingReadAccepted:
    payload_type = W24PayloadType.READ_DRAWING_INITIATED
