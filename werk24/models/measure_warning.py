
""" Defintion of all the W24MeasureWarning class its support structures


Author: Jochen Mattes - Werk24
"""
from enum import Enum
from pydantic import BaseModel


class W24MeasureWarningType(str, Enum):
    """ List of all warnings that can be associated with
    the returned measures.
    """

    UNCONVENTIONAL_TOLERANCE_ORDER = "UNCONVENTIONAL_TOLERANCE_ORDER"
    """ The UNCONVENTIONAL_TOLERANCE_ORDER warning is raised
    when the first-mentioned tolerance is lower than the second-mentioned.

    EXAMPLE: 3 -0.1/+0.1 (rather than 3 +0.1/-0.1)
    """

    UNPROPORTIONAL = "UNPROPORTIONAL"
    """ The UNPROPORTIONAL warnings is set when the size indicated
    on the MeasureLabel is unproportional to the distance between
    the Measure's end-points.
    """


class W24MeasureWarning(BaseModel):
    """ Warnings are issued when something about the label
    or measure is not conforming with convention
    """
    warning_type: W24MeasureWarningType


class W24MeasureWarningUnconvetionalToleranceOrder(W24MeasureWarning):
    """ The UNCONVENTIONAL_TOLERANCE_ORDER warning is raised
    when the first-mentioned tolerance is lower than the second-mentioned.

    EXAMPLE: 3 -0.1/+0.1 (rather than 3 +0.1/-0.1)
    """
    warning_type = W24MeasureWarningType.UNCONVENTIONAL_TOLERANCE_ORDER


class W24MeasureWarningUnproportional(W24MeasureWarning):
    """ The UNPROPORTIONAL warnings is set when the size indicated
    on the MeasureLabel is unproportional to the distance between
    the Measure's end-points.

    NOTE: Three things can cause this:
    1. The Measure is truely unpropotional and carries an associated
        indicator.

    2. The Measure is unporportional, but not indicated as such.
        Typically seen on drawings that "were modified on the fly"

    3. The size of the MeasureLabel was misread by the Werk24
        backend.

    Due to the lack of training data, we can currently not
    differentiate between case 1 and case 2. Once the training
    data suffices, this warning will be extended by boolean
    field 'indicated'.

    In addition, it is theoretically possible to estimate
    the likelihood of case 2 and case 3. If this becomes a
    true concern in your application, please reach out to us
    """
    warning_type = W24MeasureWarningType.UNPROPORTIONAL
