from decimal import Decimal
from pydantic import BaseModel


class W24Depth(BaseModel):
    """ Depth object that describes the details of the
    depth of a drilling or thread

    Attributes:
        blurb: String for human consumption

        depth: Depth of the drilling or thread in the units
            of the parent object
    """
    blurb: str

    depth: Decimal
