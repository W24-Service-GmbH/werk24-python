from decimal import Decimal
from typing import Optional

from pydantic import BaseModel

from .size import W24Size
from .unit import W24UnitAngle


class W24Chamfer(BaseModel):
    """Chamfer in degree.

    Attributes:
        blurb: String representation for human consumption

        size[Optional]: Size of chamfer as referred to in the drawing.

        angle: Chamfer angle in degrees

        unit: Angle Unit. Currently only degrees are
            supported.

    !!! note
        The chamfers can be tolerated.
        Future implementations will take this into account.

    """

    blurb: str

    angle: Decimal

    size: Optional[W24Size] = None

    unit: W24UnitAngle = W24UnitAngle.DEGREE
