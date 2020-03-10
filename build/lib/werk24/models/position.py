from pydantic import BaseModel

from .unit_position_quantity import W24UnitPositionQuantity


class W24Position(BaseModel):
    """ Position as listed on the title pages.
    See W24PositionGroup for more details
    """

    position: str
    quantity: float
    quantity_unit: str = W24UnitPositionQuantity.UNITS
