from pydantic import BaseModel

from .radius_type import W24RadiusType


class W24Radius(BaseModel):
    """ W24Radius describes a radius (e.g. for the curvature)
    of a volume shell

    The value is  measured in millimeter
    """

    value: float
    radius_type: W24RadiusType
