from enum import Enum


class W24ThreadNorm(str, Enum):
    """ Enum of supported thread norms
    """

    ISO1502 = "ISO1502"
    UNIFIED_THREAD_STANDARD = "UNIFIED_THREAD_STANDARD"
