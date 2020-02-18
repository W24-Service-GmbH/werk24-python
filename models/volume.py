from pydantic import BaseModel


class W24Volume(BaseModel):
    """ W24Volume is the base model for volumes.
    Each GeometryType derives a volume from it.
    """
    name: str
