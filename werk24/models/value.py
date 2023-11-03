from decimal import Decimal
from typing import Optional, Annotated

from pint import Quantity as PintQuantity, UnitRegistry
from pydantic import BaseModel, Field, BeforeValidator, WithJsonSchema, PlainSerializer

from werk24.models.tolerance import W24Tolerance

ureg = UnitRegistry()

Quantity = Annotated[
    PintQuantity,
    BeforeValidator(lambda x: x if isinstance(x, PintQuantity) else ureg(str(x))),
    PlainSerializer(lambda x: str(x), return_type=str),
    WithJsonSchema({"type": "string"}, mode="serialization"),
    WithJsonSchema({"type": "string"}, mode="validation"),
]


class W24PhysicalQuantity(BaseModel):
    """Physical Quantity.

    Physical Quantity with a value, unit and tolerance.
    """

    class Config:
        arbitrary_types_allowed = True

    blurb: str = Field(
        title="blurb",
        description="Blurb of the Physical Property for human consumption.",
    )
    value: Quantity = Field(
        title="value", description="Physical quantity in the string format of Pint."
    )
    tolerance: Optional[W24Tolerance] = None


class W24Value(BaseModel):
    blurb: str
    value: Decimal
    tolerance: Optional[W24Tolerance] = None
