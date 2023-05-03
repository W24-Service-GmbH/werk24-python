from typing import Any

from werk24.models.typed_model import W24TypedModel


class W24Property(W24TypedModel):
    class Config:
        discriminators = ('property_type', 'property_subtype')

    property_type: Any
    property_subtype: Any
    blurb: str
