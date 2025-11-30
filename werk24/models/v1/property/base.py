from typing import Any

from pydantic import ConfigDict

from ..typed_model import W24TypedModel


class W24Property(W24TypedModel):
    model_config = ConfigDict(discriminator="property_type")

    property_type: Any
    property_subtype: Any
    blurb: str
