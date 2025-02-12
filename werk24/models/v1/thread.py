""" Definition of the Thread support structures

Author: Jochen Mattes - Werk24
"""

import abc
from decimal import Decimal
from enum import Enum
from typing import List, Literal, Optional, Union

from pydantic import BaseModel

from .base_feature import W24BaseFeatureModel
from .fraction import W24Fraction
from .gender import W24Gender
from .tolerance import W24ToleranceType
from .unit import W24UnitLength


class W24ThreadType(str, Enum):
    """Enum for the individual thread types

    NOTE: UTS_COARSE, UTS_FINE, UTS_EXTRAFINE and UTS_SPECIAL
        as individual types will be deprecated. Their information
        individual `threads_per_inch` information will be stored
        in the corresponding variable.
    """

    ISO_METRIC = "ISO_METRIC"
    WHITWORTH = "WHITWORTH"
    UTS = "UTS"
    SM = "SM"
    NPT = "NPT"
    ACME = "ACME"
    KNUCKLE = "KNUCKLE"

    # !!! DEPRECATED
    UTS_COARSE = "UTS_COARSE"

    # !!! DEPRECATED
    UTS_FINE = "UTS_FINE"

    # !!! DEPRECATED
    UTS_EXTRAFINE = "UTS_EXTRAFINE"

    # !!! DEPRECATED
    UTS_SPECIAL = "UTS_SPECIAL"


class W24ThreadHandedness(str, Enum):
    """Enum describing the direction of the
    thread
    """

    LEFT = "LEFT"
    RIGHT = "RIGHT"


class W24ThreadMultiStart(BaseModel):
    """Multi-Start Thread Information

    A common example of multi-start threads are the cap on a plastic
    water bottle. The cap will screw on quickly because a multi-start thread.

    Attributes:

        thread_lead (Decimal, optional): Thread lead for multiple
            starts

        number_of_starts (int): Number of intertwined threads running
            in parallel to one another.

    """

    thread_lead: Optional[Decimal]
    number_of_starts: int = 1


class W24Thread(BaseModel, abc.ABC):
    """Abstract Base Class for all Threads

    Attributes:
        blurb (str): String representation of the thread for human consumption

        diameter (Decimal): Diameter of the thread

        diameter_preference: Not all Threads are made equal. The standardization
            bodies assign different preferences to the different thread diameters.

        unit (W24UnitLength): Length unit of the diameter. This allows you
            to differentiate between inch and millimeter (UTS or ISO METRIC).
            NOTE: Whitworth inch are not 2.54mm long! (for historic reasons).
            Use the whitworth_size if you need to have the Whitworth inches.

        thread_type: thread type to facilitate deserialization

        pitch: Pitch of the thread in mm. Normed range: 0.25 - 9mm
            The value will always be set - even if the pitch is give implicitly
            (e.g. M10c) or when the pitch is given in threads per inch.
            When the Pitch is ambiguous, this value be the median pitch

        threads_per_inch: Pitch and Threads per inch are interchangeable
            concepts. Depending on your geographic focus, the one or the
            other concept is more suitable. We convert ISO pitches to
            UTS threads per inch and vice versa, so that you do not have
            to handle the conversion.

        handedness: Left of right-handedness of the thread.
            This will be RIGHT unless explicitly described as LEFT
            in the drawing.

        length (Decimal, optional): Length of the Thread if specified
            on the label (e.g., M15x1x20). None otherwise.
            NOTE: If the thread length is not specified in the label, you can
            still obtain the information from the W24ThreadElement
            NOTE: If the thread label specifies both a thread length and a
            bore length, only the thread length will be included here. The
            bore length can be found in the W24MeasureElement.depth attribute
    """

    blurb: str

    diameter: Decimal

    unit: W24UnitLength = W24UnitLength.MILLIMETER

    thread_type: W24ThreadType

    pitch: Decimal

    threads_per_inch: Decimal

    handedness: W24ThreadHandedness = W24ThreadHandedness.RIGHT

    multi_start: W24ThreadMultiStart

    length: Optional[Decimal] = None


class W24ThreadISOMetricThreadEngagementClass(str, Enum):
    """Thread Engagement in accordance with ISO 965-1:1998"""

    SHORT = "SHORT"
    NORMAL = "NORMAL"
    LONG = "LONG"


class W24ThreadISOMetric(W24Thread):
    """Metric ISO Thread following ISO 1502

    Supports
    * DIN 14-1 threads (i.e., diameter < 1mm)
    * DIN 13-1 threads (i.e., diameter 1..68mm)
    * DIN 13-2 to DIN 13-10 threads (i.e., diameter 1..1000mm)
    * DIN 158-1 (i.e., cone-shaped threads)

    NOTE: ISO 965-1:1998 allows for the specification of fits
    between threaded parts. This is considered by giving access
    to all internal and external tolerance parameters.

    Attributes:
        inner_major_diameter_tolerance (str): Tolerance Class
            for the major diameter in accordance with ISO 965-1.
            None if the major diameter tolerance class is neither
            defined in the standard not explicitly specified

        inner_pitch_diameter_tolerance (str): Tolerance Class
            for the pitch diameter in accordance with ISO 965-1.
            None if the pitch diameter tolerance class is neither
            defined in the standard not explicitly specified

        outer_major_diameter_tolerance (str): Corresponding
            tolerance class for the major diameter of the
            outer thread

        outer_pitch_diameter_tolerance (str): Corresponding
            tolerance class for the pitch diameter of the outer thread.

    """

    thread_type: Literal[W24ThreadType.ISO_METRIC] = W24ThreadType.ISO_METRIC

    female_major_diameter_tolerance: Optional[W24ToleranceType]
    female_pitch_diameter_tolerance: Optional[W24ToleranceType]
    male_major_diameter_tolerance: Optional[W24ToleranceType]
    male_pitch_diameter_tolerance: Optional[W24ToleranceType]


class W24ThreadSM(W24Thread):
    """Sewing Machine Threads (SM)
        SM thread is used in sewing machine,
        recently it is also being used in Optical Industry.

    Attributes:
        sm_size: Only few sizes are available (05,1,1.5,2,3)
            Examples: SM05, SM1, etc

        threads_per_inch: Threads per inch is fixed to 40.

    """

    thread_type: Literal[W24ThreadType.SM] = W24ThreadType.SM

    sm_size: Decimal


class W24ThreadUTS(W24Thread):
    """Unified Thread Standard (UTS) base class for
    * UNC - Unified National Coarse Thread
    * UNF - Unified National Fine Thread
    * UNEF - Unified National Extrafine Thread

    Attributes:
        uts_size: UTS size as string representation.
            Threads with a diameter < 0.25 inch are written with a leading '#'.
            Threads with a diameter >= 0.25 inch are represented as fractions
                with a tailing '"'
            Examples: #0, 1 3/4"

        uts_series (str): UTS Forma n series following ASME B1.1 2003.
            Valid values include UNC UNF, UNRF, UNF, UN

        threads_per_inch: Threads per inch. The Decimal (rather than int)
            is chosen to support non-conventional threads.

        tolerance_class: Tolerance class. Options:
            * 1A, 2A, 3A for external threads
            * 1B, 2B, 3B for internal threads
    """

    thread_type: Literal[W24ThreadType.UTS] = W24ThreadType.UTS

    uts_size: str
    uts_series: str

    tolerance_class: str


class W24ThreadACME(W24Thread):
    """American Corps of Mechanical Engineering (ACME)  defines
    * ACME - American Corps of Mechanical Engineering Thread
    * STUB ACME - STUB American Corps of Mechanical Engineering Thread

    Attributes:
        acme_size: ACME size as string representation.
            Threads diameter in inch are represented as decimal or fractions
                with a tailing '"'
            Examples: 2", 1 3/4"

        acme_series (str): ACME series following ASME B1.8-1977.
            Valid values include ACME, STUB ACME

        threads_per_inch: Threads per inch. can be Decimal / Fraction.

    """

    thread_type: Literal[W24ThreadType.ACME] = W24ThreadType.ACME

    acme_size: str
    acme_series: str


class W24ThreadNPT(W24Thread):
    """American National Standard Pipe Thread standards,
        often called National Pipe Thread (NPT) standards.
    * NPT - National pipe taper
    * NPS - National pipe straight

    Attributes:
        npt_size: NPT size as string representation.
            Threads diameter in inch are represented as decimal or fractions
                with a tailing '"'
            Examples: 2", 1 3/4"

        npt_series (str): NPT series following ANSI B 1.20.1.
            Valid values include NPT, NPTF, NPSC, NPSF, NPSL, NPSM

        threads_per_inch: Threads per inch. can be Decimal / Fraction.

    """

    thread_type: Literal[W24ThreadType.NPT] = W24ThreadType.NPT

    npt_size: str
    npt_series: str


class W24ThreadUTSCoarse(W24ThreadUTS):
    """Unified National Coarse Thread

    NOTE: will be deprecated in favor of W24ThreadUTS
    """

    thread_type: Literal[W24ThreadType.UTS_COARSE] = W24ThreadType.UTS_COARSE


class W24ThreadUTSFine(W24ThreadUTS):
    """Unified National Fine Thread

    NOTE: will be deprecated in favor of W24ThreadUTS
    """

    thread_type: Literal[W24ThreadType.UTS_FINE] = W24ThreadType.UTS_FINE


class W24ThreadUTSExtrafine(W24ThreadUTS):
    """Unified National Extrafine Thread

    NOTE: will be deprecated in favor of W24ThreadUTS
    """

    thread_type: Literal[W24ThreadType.UTS_EXTRAFINE] = W24ThreadType.UTS_EXTRAFINE


class W24ThreadUTSSpecial(W24ThreadUTS):
    """Unified National Special Thread

    NOTE: will be deprecated in favor of W24ThreadUTS
    """

    thread_type: Literal[W24ThreadType.UTS_SPECIAL] = W24ThreadType.UTS_SPECIAL


class W24ThreadWhitworth(W24Thread):
    """Whitworth Thread following ISO 228-1

    Attributes:
        whitworth_size: Size number (for historic reasons
            not proportional to size)

        tolerance_class: Tolerance field

    """

    thread_type: Literal[W24ThreadType.WHITWORTH] = W24ThreadType.WHITWORTH

    whitworth_size: Decimal

    tolerance_class: Optional[str] = None


class W24ThreadKnuckle(W24Thread):
    """Knuckle Thread following DIN 405 or DIN 20400

    Attributes:
        knuckle_profile: Profile of the Knuckle Threads
            is a fraction that defines the pitch for
            the thread. Applicable to knuckle threads
            following DIN 405.

    """

    thread_type: W24ThreadType = W24ThreadType.KNUCKLE

    knuckle_size: str
    knuckle_series: str
    knuckle_profile: Optional[W24Fraction] = None


class W24ThreadFeature(W24BaseFeatureModel):
    """Characterization of a Thread Feature

    Attributes:
        gender (Optional[W24Gender]): Gender (male or female) of the thread feature.
            This is determined by checking whether the thread is
            located on the outer contour of the part or inside the part.
            When the outer contour is unavailable (e.g., in detail drawings),
            the gender is set to None.

        length (Optional[Decimal]): Length of the slug corresponding
            to the thread. Please keep in mind that a thus can
            contain multiple threads with different lengths. This
            is considered in the threads themselves.
            NOTE: we are using the word length here to differentiate
            it from the thread depth which describes the difference
            between the major and minor radii.

        threads (List[W24Thread]): List of Threads that are positioned
            on the ThreadFeatures. This is a list to support multi-threads

    """

    gender: Optional[W24Gender]

    length: Optional[Decimal]

    threads: List[W24Thread]


W24ThreadUnion = Union[
    W24ThreadACME,
    W24ThreadISOMetric,
    W24ThreadKnuckle,
    W24ThreadNPT,
    W24ThreadSM,
    W24ThreadUTS,
    W24ThreadWhitworth,
]
