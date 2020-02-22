from typing import Optional
from pydantic import BaseModel, UUID4


class W24DrawingReadResponse(BaseModel):
    request_id: UUID4
    error: Optional[str] = None
