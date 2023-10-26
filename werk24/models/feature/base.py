from typing import Optional, Any

from pydantic import BaseModel

from werk24.models.standard import W24Standard


class W24Feature(BaseModel):
    """BaseModel for all Werk24 Features.

    Attributes:
        blurb (str): Description of the feature
            following the logic of the referenced
            standard. If no standard is references,
            we fall back to the ISO way of doing things.
            See ISO 19136-1:2020.

        standard (Optional[W24Standard]): if available,
            the standard that defines the feature.
    """

    blurb: str
    feature_type: Any
    feature_subtype: Any = None
    standard: Optional[W24Standard] = None
