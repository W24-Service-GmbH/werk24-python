""" Definition of the Thread support structures

Author: Jochen Mattes - Werk24
"""
import abc
from decimal import Decimal
from enum import Enum
from typing import Optional

from pydantic import BaseModel

from .unit import W24UnitLength


class W24ThreadType(str, Enum):
    """ Enum for the individual thread types
    """
    ISO_METRIC = "ISO_METRIC"
    WHITWORTH = "WHITWORTH"
    UTS_COARSE = "UTS_COARSE"
    UTS_FINE = "UTS_FINE"
    UTS_EXTRAFINE = "UTS_EXTRAFINE"
    UTS_SPECIAL = "UTS_SPECIAL"


class W24ThreadHandedness(str, Enum):
    """ Enum describing the direction of the
    thread
    """
    LEFT = "LEFT"
    RIGHT = "RIGHT"


class W24Thread(BaseModel, abc.ABC):
    """ Abstract Base Class for all Threads

    Attributes:
        blurb (str): String representation of the thread for human consumption

        diameter (Decimal): Diameter of the thread

        unit (W24UnitLength): Length unit of the diameter. This allows you
            to differentiate between inch and millimeter (UTS or ISO METRIC).

            NOTE: Whitworth inch are not 2.54mm long! (for historic reasons).
            Use the whitworth_size if you need to have the whitworth inches.

        thread_type (W24Thread): thread type to facilitate deserialization

        handedness: Left of right-handedness of the thread.
            This will be RIGHT unless explicitly described as LEFT
            in the drawing.

    """
    blurb: str

    diameter: Decimal

    unit: W24UnitLength = W24UnitLength.MILLIMETER

    thread_type: W24ThreadType

    handedness: W24ThreadHandedness = W24ThreadHandedness.RIGHT


class W24ThreadISOMetric(W24Thread):
    """ Metric ISO Thread following ISO 1502

    Supports
    * DIN 14-1 threads (i.e., diameter < 1mm)
    * DIN 13-1 threads (i.e., diameter 1..68mm)
    * DIN 13-2 to DIN 13-10 threads (i.e., diameter 1..1000mm)
    * DIN 158-1 (i.e., cone-shaped threads)

    Attributes:

        pitch: Pitch of the thread in mm. Normed range: 0.25 - 9mm
            The value will only be set if is explicitly
            stated in the drawing. This behaviour might change
            in the future and perform an automatic lookup in the
            DIN standards. If this change would affect your
            application, please get in touch with us.
    """
    thread_type = W24ThreadType.ISO_METRIC

    pitch: Optional[Decimal] = None


class W24ThreadUTS(W24Thread):
    """ Unified Thread Standard (UTS) base class for
    * UNC - Unified National Coarse Thread
    * UNF - Unified National Fine Thread
    * UNEF - Unified National Extrafine Thread

    Attributes:
        uts_size: UTS size as string representation.
            Threads with a diameter < 0.25 inch are written with a leading '#'.
            Threads with a diameter >= 0.25 inch are represented as fractions
                with a tailing '"'
            Examples: #0, 1 3/4"

        threads_per_inch: Threads per inch. The Decimal (rather than int)
            is chosen to support non-conventional threads.

        tolerance_class: Tolerance class. Options:
            * 1A, 2A, 3A for external threads
            * 1B, 2B, 3B for internal threads
    """
    uts_size: str

    threads_per_inch: Decimal

    tolerance_class: str


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

    Attributes:
        whitworth_size: Size number (for historic reasons
            not proportional to size)

        tolerance_class: Tolerance field

    """
    thread_type = W24ThreadType.WHITWORTH

    whitworth_size: Decimal

    tolerance_class: Optional[str] = None
