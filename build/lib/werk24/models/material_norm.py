from enum import Enum


class W24MaterialNorm(str, Enum):
    """ Enum of supported material norms
    """

    EN10025 = "EN10025"
    DIN17100 = "DIN17100"
    SAE = "SAE"
