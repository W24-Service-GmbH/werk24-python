from enum import Enum


class W24Architecture(str, Enum):
    """ List of available architectures.
    Beware that chosing a different architecture
    will have effects on both the speed and
    the cost of your request.

    By default only CPU_V1 is available to new users.
    Please talk to us if you have other requirements.
    """
    CPU_V1 = "CPU_V1"
