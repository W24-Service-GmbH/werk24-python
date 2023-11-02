from decimal import Decimal

from pydantic import BaseModel

from .unit import W24UnitAngle


class W24Chamfer(BaseModel):
    """Chamfer in degree.

    Attributes:
        blurb: String representation for human consumption

        angle: Chamfer angle in degrees

        unit: Angle Unit. Currently only degrees are
            supported.

    !!! note
        The chamfers can be tolerated.
        Future implementations will take this into account.

    """

    blurb: str

    angle: Decimal

    unit: W24UnitAngle = W24UnitAngle.DEGREE
