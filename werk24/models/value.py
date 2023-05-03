from decimal import Decimal
from typing import Optional, Union

from pint import Quantity, UnitRegistry
from pydantic import BaseModel, validator

from werk24.models.tolerance import W24Tolerance

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

    @validator('value', pre=True)
    def value_validation(cls, value: Union[str, Quantity]) -> Quantity:
        """Perform the de-serialization of the value.

        Follow the recommendations of pint for (de-)
        serialization. See https://pint.readthedocs.io/en/0.10.1/serialization.html

        Args:
            value (Union[str, Quantity]): Raw value

        Returns:
            Quantity: Deserialized version of the quantity.
        """
        if isinstance(value, Quantity):
            return value
        return ureg(value)

    blurb: str
    value: Quantity
    tolerance: Optional[W24Tolerance] = None


class W24Value(BaseModel):
    blurb: str
    value: Decimal
    tolerance: Optional[W24Tolerance] = None
