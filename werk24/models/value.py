from decimal import Decimal
from typing import Optional

from pint import Quantity, UnitRegistry
from pydantic import BaseModel

ureg = UnitRegistry()


class W24PhysicalQuantity(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    value: Quantity

    def __str__(self) -> str:
        return str(self.value)


class W24PhysicalQuantityRange(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    min_value: Quantity
    max_value: Optional[Quantity]

    def __str__(self) -> str:
        if self.max_value is None:
            return str(self.min_value)
        return f"{self.min_value} - {self.max_value}"


class W24ValueRange(BaseModel):
    min_value: Decimal
    max_value: Decimal


class W24Value(BaseModel):
    value: Decimal
