from .ask import W24Ask
from .ask_type import W24AskType


class W24AskMeasures(W24Ask):
    """ Requesting the W24AskMeasures will add
    a list of all detected measures to the result
    """
    ask_type = W24AskType.MEASURES
