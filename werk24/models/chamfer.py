""" A chamfer is a transitional edge between two faces of an object.
It is attached to the W24MeasureLabel and typically indicates an
angle of 30 or 45 degrees.
"""
from pydantic import BaseModel

from .unit import W24UnitAngle


class W24Chamfer(BaseModel):
    """ Chamfer in degree.

    Attributes:
        blurb: String representation for human consumption

        angle: Chamfer angle in degrees

        unit: Angle Unit. Currently only degrees are
            supported.

    !!! note
        The chamfers can be tolerated.
        Future implementations will take this into account.

    !!! NOTE
        If you are dealing with GON, let us know.
        Happy to do exend the API for the pleasure of
        dealing with the concept.
    """

    blurb: str

    angle: float

    unit: W24UnitAngle = W24UnitAngle.DEGREE
