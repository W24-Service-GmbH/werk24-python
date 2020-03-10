from pydantic import BaseModel

from .material_norm import W24MaterialNorm


class W24MaterialNormed(BaseModel):
    """ W24MaterialNormed describes a material as defined
    by a standardization body.

    NOTE: Werk24 makes an effort to map material names from
    deprecated norms to the most recent standard in each
    geography.
    """

    name: str
    norm: W24MaterialNorm = W24MaterialNorm.EN10025
