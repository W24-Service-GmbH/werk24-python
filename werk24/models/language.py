from enum import Enum


class W24Language(str, Enum):
    """ Enum of supported languages following
    the naming convention of ISO/639-2B
    """

    FRE = "FRE"
    """ French """

    GER = "GER"
    """ German """

    ENG = "ENG"
    """ English """
