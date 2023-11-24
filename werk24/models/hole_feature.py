from decimal import Decimal
from typing import Optional

from pydantic import BaseModel

from .size import W24Size
from .depth import W24Depth
from .tolerance import (
    W24ToleranceType,
    W24ToleranceGeneral,
)


class W24CounterBore(BaseModel):
    """Size of the Counterbore including its angle

    Attributes:
        blurb: Blurb for human consumption
        size: Size of the Counterbore as referred in the hole callout.
        depth: Depth of the Counterbore
    """

    blurb: str
    size: W24Size
    depth: W24Depth
    size_tolerance: W24ToleranceType = W24ToleranceGeneral()


class W24CounterDrill(BaseModel):
    """Size of the Counter Drill including its angle

    Attributes:
        blurb: Blurb for human consumption
        size: Size of the Counterdrill as referred in the hole callout.
        depth: Depth of the Counterdrill
        angle: Angle of the Counterdrill in Degrees. Angle of counterdrill
            is preferred to be annotated in a sectional view of the hole.
            As a result, angle is optional and set to None by default.
    """

    blurb: str
    size: W24Size
    depth: W24Depth
    angle: Optional[Decimal] = None
    size_tolerance: W24ToleranceType = W24ToleranceGeneral()


class W24CounterSink(BaseModel):
    """Size of the Countersink including its angle

    Attributes:
        blurb: Blurb for human consumption
        size: Size of the Countersink as referred in the hole callout.
        angle: Angle of the Countersink in Degrees
    """

    blurb: str
    size: W24Size
    angle: Decimal
    size_tolerance: W24ToleranceType = W24ToleranceGeneral()
