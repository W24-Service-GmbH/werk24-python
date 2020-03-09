from pydantic import BaseModel
from typing import List, Dict
from .attachment import W24Attachment
from .part import W24Part
from .position_group import W24PositionGroup


class W24Document(BaseModel):
    """ The W24Document is the main response document
    and acts as container for all parts
    """

    parts: List[W24Part] = []
    attachments: Dict[str, W24Attachment] = {}
    request_id: str
    unassociated_position_groups: List[W24PositionGroup] = []
