
""" Defintion of all the W24Measure class its support structures


Author: Jochen Mattes - Werk24
"""
from typing import List, Optional, Tuple

from pydantic import BaseModel, UUID4

from .measure_warning import W24MeasureWarning
from .thread import W24Thread
from .unit import W24UnitLength
from .size_tolerance import W24SizeTolerance, W24SizeToleranceGeneral
from .chamfer import W24Chamfer
from .size import W24Size


class W24MeasureLabel(BaseModel):
    """ Abstract base class for all MeasureItem Children
    """

    blurb: str
    """ String representation of the item for human consumption
    """

    quantity: int = 1
    """ Quantity for spacings
    e.g., (2x)

    NOTE: Currently only the indicated measure will be detected and
    returned. Future implementation could detect the spacings and
    return individual measures for the respective spacings.
    When we implement this feature, we will add an attribute to the
    ASK, which allows you to control the behavior.
    """

    size: W24Size
    """ Size of measure as refered to in the drawing.

    NOTE: Sizes are always assocated with units! This becomes important
    to remember when you are dealing with mixed-unit drawings (e.g.,
    an adapter bolt that has an ISO thread and an UTC tapped hole).
    To avoid any loss of precision, we return the size in the unit
    that was indicated on the drawing.
    """

    unit: Optional[W24UnitLength] = None
    """ Length unit of the size
    """

    size_tolerance: W24SizeTolerance = W24SizeToleranceGeneral()
    """ Tolerance details.
    Default: General tolerances

    NOTE: by default we are refering to the general tolerances of the drawing.
    Currently the W24SizeToleranceGeneral object is a stub.
    Future implementations might go one step further and quote the
    applicable general tolerance as refered to in the data fields.

    NOTE: if the W24MeasureLabel describes a "Theoretically Exact Measure",
    i.e, the label is surrounded by a box, like: "[15]", the size_tolerance
    refers to a W24SizeToleranceTheoreticallyExact object (and is NOT None)
    """

    thread: Optional[W24Thread] = None
    """ Optional thread details.

    NOTE: the thread details describe the complete thread description
    and follow the respective standards. In consequence, the thread
    diameter of an ISO-thread will be indicated in millimeter,
    while the thread diameter of an UTS thread will be in inch.

    """

    chamfer: Optional[W24Chamfer] = None
    """ Optional Chamfer
    """


class W24Measure(BaseModel):
    """ Tolerated measure
    """

    measure_id: Optional[UUID4] = None
    """ Unique id of measure
    """

    line: Tuple[Tuple[float, float], Tuple[float, float]]
    """ Tuple of the measure's start- and end-coordinates
    in the Pixel Coordinate system of the sectional.

    The coordinates are normalized by the width and height of the
    associated object (e.g., the sectional). If you want to obtain
    the absolute position in the original image, you need to consider
    the following offsets: sectional + canvas + sheet.
    """

    label: W24MeasureLabel
    """ Measure Label
    """

    warnings: List[W24MeasureWarning] = []
    """ List of Warnings that are associated with the
    measure. See W24MeasureWarning for details
    """

    confidence: float = 0.0
    """ Werk24 calculates an internal confidence score for
    each measure. Depending on your use-case, you might want
    to consider or discard low-confidence measures. This
    value allows you to do so. The value ranges from
    0.0 to 1.0
    """
