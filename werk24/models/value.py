from decimal import Decimal
from typing import Optional

from pint import Quantity, UnitRegistry
from pydantic import BaseModel

from werk24.models.size import W24SizeTolerance

ureg = UnitRegistry()


class W24PhysicalQuantity(BaseModel):
    """Physical Quantity.

    Physical Quantity with a value, unit and tolerance.

    Attributes:
        blurb (str): Blurb of the Physical Property for
            human consumption.
        value (Quantity): Physical quantity in the string
            format of pint.
        tolerance (Optional[W24Tolerance]): Tolerance
    """
    class Config:
        arbitrary_types_allowed = True

    blurb: str
    value: Quantity
    tolerance: Optional[W24SizeTolerance] = None


class W24Value(BaseModel):
    blurb: str
    value: Decimal
    tolerance: Optional[W24SizeTolerance] = None
