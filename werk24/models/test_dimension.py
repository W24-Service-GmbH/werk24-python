from decimal import Decimal
from typing import Optional
from pydantic import BaseModel
from enum import Enum


class W24TestCriticality(str, Enum):
    CRITICAL_TO_DELIVERY = "CTD"
    CRITICAL_TO_FUNCTION = "CTF"
    CRITICAL_TO_PRICE = "CTP"
    CRITICAL_TO_QUALITY = "CTQ"
    CRITICAL_TO_SAFETY = "CTS"


class W24TestDimension(BaseModel):
    """ Test Dimension attributes that can either be attached
    to a MeasureLabel or a GDTLabel

    Attributes:
        blurb: Blurb of the complete label for human consumption

        criticality: Some measures can be critical to Function,
            others critical to price. The TestDimensions sometimes
            highlight this with a shorthand (e.g., CTF)

        rate: Test rate as percentage. If a 100% inspection rate has been
            defined, rate will be Decimal('100'). If not defined, the
            rate will be None.
    """
    blurb: str
    criticality: Optional[W24TestCriticality] = None
    rate: Optional[Decimal] = None
