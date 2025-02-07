from enum import Enum


class W24Language(str, Enum):
    """Enum of supported languages following
    the naming convention of ISO/639-2B
    """

    DEU = "DEU"
    """ German """

    DUT = "DUT"
    """ Dutch """

    ENG = "ENG"
    """ English """

    FRA = "FRA"
    """ French """

    ITA = "ITA"
    """ Italian """

    SPA = "SPA"
    """ Spanish """

    UNKNOWN = "__UNK__"
    """ Unknown """
