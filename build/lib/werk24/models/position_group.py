from typing import List

from pydantic import BaseModel

from .position import W24Position


class W24PositionGroup(BaseModel):
    """ A W24PositionGroup contains all position information
    for a given part
    """

    positions: List[W24Position]
    article_number: str
    description: str
