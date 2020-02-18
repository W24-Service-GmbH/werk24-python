from pydantic import BaseModel, UUID4


class W24IoResponse(BaseModel):
    request_id: UUID4
