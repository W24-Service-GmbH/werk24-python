import abc
from typing import Any

from pydantic import BaseModel


class W24Property(BaseModel, abc.ABC):
    blurb: str
    property_type: Any
    property_subtype: Any
