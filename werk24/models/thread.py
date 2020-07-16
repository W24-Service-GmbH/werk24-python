""" Definition of the Thread support structures

Author: Jochen Mattes - Werk24
"""
from enum import Enum
from pydantic import BaseModel
from typing import Optional
import abc


class W24ThreadType(str, Enum):
    """ Enum for the individual thread types
    """
    ISO_METRIC = "ISO_METRIC"
    WHITWORTH = "WHITWORTH"
    UTS_COARSE = "UTS_COARSE"
    UTS_FINE = "UTS_FINE"
    UTS_EXTRAFINE = "UTS_EXTRAFINE"
    UTS_SPECIAL = "UTS_SPECIAL"


class W24Thread(BaseModel, abc.ABC):
    """ Abstract Base Class for all Threads
    """

    thread_type: W24ThreadType
    """ thread type to facilitate deserialization
    """

    blurb: str
    """ string representation for human interpretation
    """


class W24ThreadHandedness(str, Enum):
    """ Enum describing the direction of the
    thread
    """
    LEFT = "LEFT"
    RIGHT = "RIGHT"


class W24ThreadISOMetric(W24Thread):
    """ Metric ISO Thread following ISO 1502

    Supports
    * DIN 14-1 threads (i.e., diameter < 1mm)
    * DIN 13-1 threads (i.e., diameter 1..68mm)
    * DIN 13-2 to DIN 13-10 threads (i.e., diameter 1..1000mm)
    * DIN 158-1 (i.e., cone-shaped threads)
    """
    thread_type = W24ThreadType.ISO_METRIC

    diameter: float
    """ Diameter of the thread in mm.

    NOTE: The norms range from 0.1 to 1000mm;
    however, diameters outside that range are possible
    (and occur)
    """

    pitch: Optional[float] = None
    """ Pitch of the thread in mm.
    Normed range: 0.25 - 9mm

    NOTE: the value will only be set if is explicitly
    stated in the drawing. This behaviour might change
    in the future and perform an automatic lookup in the
    DIN standards. If this change would affect your
    application, please get in touch with us.
    """

    # shape: W24ThreadMetricISOShape
    """ NOTE: cone-shaped threads identified by a 'keg' suffix
    are currently not supported.
    """  # pylint: disable=pointless-string-statement

    handedness: W24ThreadHandedness = W24ThreadHandedness.RIGHT
    """ Left of right-handedness of the thread.
    This will be RIGHT unless explicitly described as LEFT
    in the drawing
    """


class W24ThreadUTS(W24Thread):
    """ Unified Thread Standard (UTS) base class for
    * UNC - Unified National Coarse Thread
    * UNF - Unified National Fine Thread
    * UNEF - Unified National Extrafine Thread
    """

    uts_size: str
    """ UTS size as string representation.
    Threads with a diameter < 0.25 inch are written with a leading '#'.
    Threads with a diameter >= 0.25 inch are represented as fractions
        with a tailing '"'
    Examples: #0, 1 3/4"
    """

    diameter: float
    """ diameter in inch derived from the unc_size
    """

    threads_per_inch: float
    """ Threads per inch
    NOTE: The float (rather than int) is chosen to support non-convertional
    threads as well.
    """

    tolerance_class: str
    """ Tolerance class
    Options:
    * 1A, 2A, 3A for external threads
    * 1B, 2B, 3B for internal threads
    """


class W24ThreadUTSCoarse(W24ThreadUTS):
    """ Unified National Coarse Thread
    """
    thread_type = W24ThreadType.UTS_COARSE


class W24ThreadUTSFine(W24ThreadUTS):
    """ Unified National Fine Thread
    """
    thread_type = W24ThreadType.UTS_FINE


class W24ThreadUTSExtrafine(W24ThreadUTS):
    """ Unified National Extrafine Thread
    """
    thread_type = W24ThreadType.UTS_EXTRAFINE


class W24ThreadUTSSpecial(W24ThreadUTS):
    """ Unified National Special Thread
    """
    thread_type = W24ThreadType.UTS_SPECIAL


class W24ThreadWhitworth(W24Thread):
    """ Whitworth Thread following ISO 228-1
    """
    thread_type = W24ThreadType.WHITWORTH

    whitworth_size: float
    """ Size number (for historic reasons not proportional to size)
    """

    tolerance_class: Optional[str] = None
    """ Tolerance field A implemented in the future
    """  # pylint: disable=pointless-string-statement
