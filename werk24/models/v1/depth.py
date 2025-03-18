from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class W24DepthThroughType(str, Enum):
    """Through Type specified on ASME drawings."""

    THRU = "THRU"
    THRU_ALL = "THRU_ALL"
    BLIND = "BLIND"


class W24Depth(BaseModel):
    """Depth object that describes the details of the
    depth of a drilling or thread

    Attributes:
        blurb: String for human consumption

        depth: Depth of the drilling or thread in the units
            of the parent object
    """

    blurb: str

    depth: Optional[Decimal] = None

    through_type: Optional[W24DepthThroughType] = None
