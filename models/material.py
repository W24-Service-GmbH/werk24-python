from pydantic import BaseModel

from .material_shape import W24MaterialShape


class W24Material(BaseModel):
    """ W24Material describes the shape and type of material
    from which a part is to be produced.

    NOTE: The blob holds the material name as quoted in the document.
    """
    designation: str
    shape: W24MaterialShape = None
