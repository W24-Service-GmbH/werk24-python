from pydantic import BaseModel

from .illustration_type import W24IllustrationType


class W24Illustration(BaseModel):
    """ W24Illustration associates an attachment by its
    attachment_hash to a W24Part
    """

    attachment_hash: str
    illustration_type: W24IllustrationType
