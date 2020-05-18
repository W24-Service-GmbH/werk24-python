""" Defintion of all the W24Measure object and all its requirements.

"""
from enum import Enum
from typing import Optional, Tuple, List

from pydantic import BaseModel


class W24MeasureThreadType(str, Enum):
    """ Enum capturing all supported Thread Types
    """

    METRIC_STANDARD_THREAD = "METRIC_STANDARD_THREAD"
    """ Metric Standard Thread
    (typically indicated by an 'M'-prefix
    """


class W24MeasureThreadHandedness(str, Enum):
    """ Enum describing the direction of the
    thread
    """

    LEFT = "LEFT"
    """ Left-handed Thread
    """

    RIGHT = "RIGHT"
    """ Right-handed Thread
    """


class W24MeasureWarningType(str, Enum):
    """ List of all warnings that can be associated with
    the returned measures.
    """

    UNCONVENTIONAL_TOLERANCE_ORDER = "UNCONVENTIONAL_TOLERANCE_ORDER"
    """ The UNCONVENTIONAL_TOLERANCE_ORDER warning is raised
    when the first-mentioned tolerance is lower than the second-mentioned.
    Example: 3 -0.1/+0.1 (rather than 3 +0.1/-0.1)
    """


class W24MeasureWarning(BaseModel):
    """ Warnings are issued when something about the label
    or measure is not conforming with convention
    """
    warning_type: W24MeasureWarningType


class W24Measure(BaseModel):
    """ Tolerated measure with positve and negative tolerances.
    All measures are in Millimeter

    NOTE: Fit measures are translated into positive and
    negative tolerances.
    """

    line: Tuple[Tuple[float, float], Tuple[float, float]]
    """ Relative x-y coordinates of the Start/End point of the Measure in the
    Pixel Coordinate system that the Measure is associated to.
    Typically this will be the W24AskVariantMeasuresResponse.

    The coordinates are normalized by the width and height of the
    associated object (e.g., the sectional). If you want to obtain
    the absolute position in the original image, you need to consider
    the following offsets: sectional + canvas + sheet.
    """

    label: str
    """ String representation of the label for human consumption
    """

    size: float
    """ Size of the measure as (signed) float in mm.

    NOTE: For Wrench_sizes this will reflect the actual distance
    that the measure describes even if the label reads "SW...",
    but is associated with the short edge distance

    NOTE: For Whitworth_sizes this will reflect the associacted
    value in mm. If you want to obtain the whitworth_size in inches,
    you'll find it in the whitworth_size
    """

    fit_size: Optional[str] = None
    """ Fit size according to ISO 286-1 / ISO 286-2.

    NOTE: this value will only be set when the technical
    drawing explicitly states it. The API does not translate
    tolerance groups into fit_size equivalents.
    """

    tolerance_upper: Optional[float] = None
    """ Signed upper tolerance as stated in the drawing.

    NOTE: When a fit size is present, this tolerance will be
    unset. If you need the API to behave in a different way,
    please get in touch with a suggestion how to handle
    inconsistencies between the tolerances and the fit_size
    """

    tolerance_lower: Optional[float] = None
    """ Lower Tolerance (See tolerance_upper) """

    chamfer_angle: Optional[float] = None
    """ Chamfer angle in degree as indicated on the label
    """

    wrench_size: Optional[float] = None
    """ Wrench Size in mm
    """

    whitworth_size: Optional[float] = None
    """ Whitworth Size in inch
    """

    thread_type: Optional[W24MeasureThreadType] = None
    """ Thread type described by the measure
    """

    thread_pitch: Optional[float] = None
    """ Thread pitch in mm.
    """

    thread_handedness: Optional[W24MeasureThreadHandedness] = None
    """ Handedness of the thread. Defaults to RIGHT if not
    explicitly stated on the drawing
    """

    warnings: List[W24MeasureWarning] = []
    """ List of Warnings that are associated with the
    measure. See W24MeasureWarning for details
    """
