from pydantic import BaseModel


class W24DrawingReadMessage(BaseModel):

    action: str
    message: str
