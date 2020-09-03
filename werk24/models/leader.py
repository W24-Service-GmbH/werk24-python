
""" Defintion of all the W24Measure class its support structures


Author: Jochen Mattes - Werk24
"""
from typing import List, Tuple

from pydantic import BaseModel, UUID4


class W24LeaderLabel(BaseModel):
    blurb: str
    """ Uninterpreted string representation of the leader
    """


class W24Leader(BaseModel):
    """ Leaders indicate which location
    """

    leader_id: UUID4
    """ Unique id of the leader
    """

    anchor_coordinates: List[Tuple[float, float]]
    """
    List of x,y tuples indicating the coordinates that
    are referenced by the leader. Be aware that leaders
    can be associated with a multitude of points.
    The x,y coordinates are normalized by the widht/height
    of the sectional image
    """

    text_coordinate: Tuple[float, float]
    """ Tuple indicating the bottom left corner of the
    leader's text box. The value is normalized by the width/heights
    of the sectional image
    """

    label: W24LeaderLabel
    """ Leader label
    """

    associated_measure_ids: List[UUID4] = []
    """ UUID List of measures that were derived from the
    current leader. Refer to W24Measure
    """
