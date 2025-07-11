""" Defintion of all the W24Measure class its support structures
"""

from enum import Enum
from typing import List, Optional

from pydantic import UUID4, BaseModel, Field, field_validator

from .base_feature import W24BaseFeatureModel
from .chamfer import W24Chamfer
from .depth import W24Depth
from .hole_feature import W24CounterBore, W24CounterDrill, W24CounterSink
from .size import W24Size
from .test_dimension import W24TestDimension
from .thread import W24ThreadUnion
from .tolerance import W24Tolerance, W24ToleranceGeneral, W24ToleranceType
from .unit import W24UnitLength


class W24MeasureWarningType(str, Enum):
    """
    List of all warnings that can be associated with
    the returned measures.
    """

    UNCONVENTIONAL_TOLERANCE_ORDER = "UNCONVENTIONAL_TOLERANCE_ORDER"
    """
    The UNCONVENTIONAL_TOLERANCE_ORDER warning is raised
    when the first-mentioned tolerance is lower than the second-mentioned.

    EXAMPLE: 3 -0.1/+0.1 (rather than 3 +0.1/-0.1)
    """

    UNPROPORTIONAL = "UNPROPORTIONAL"
    """
    The UNPROPORTIONAL warnings is set when the size indicated
    on the MeasureLabel is unproportional to the distance between
    the Measure's end-points.
    """


class W24MeasureWarning(BaseModel):
    """
    Warnings are issued when something about the label
    or measure is not conforming with convention
    """

    warning_type: W24MeasureWarningType


class W24MeasureWarningUnconvetionalToleranceOrder(W24MeasureWarning):
    """
    The UNCONVENTIONAL_TOLERANCE_ORDER warning is raised
    when the first-mentioned tolerance is lower than the second-mentioned.

    EXAMPLE: 3 -0.1/+0.1 (rather than 3 +0.1/-0.1)
    """

    warning_type: W24MeasureWarningType = (
        W24MeasureWarningType.UNCONVENTIONAL_TOLERANCE_ORDER
    )


class W24MeasureWarningUnproportional(W24MeasureWarning):
    """
    The UNPROPORTIONAL warnings is set when the size indicated
    on the MeasureLabel is unproportional to the distance between
    the Measure's end-points.

    !!! note Three things can cause this:

    1. The Measure is truly unpropotional and carries an associated
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

    warning_type: W24MeasureWarningType = W24MeasureWarningType.UNPROPORTIONAL


class W24MeasureLabel(BaseModel):
    """Measure Label

    Attributes:

        blurb: String representation of the item for human consumption

        quantity: Quantity for spacings, e.g., (2x). Currently only the
            indicated measure will be detected and returned. Future
            implementation could detect the spacings and return individual
            measures for the respective spacings. When we implement this
            feature, we will add an attribute to the ASK, which allows you
            to control the behavior.

        size: Size of measure as referred to in the drawing.
            Sizes are always associated with units! This becomes important
            to remember when you are dealing with mixed-unit drawings (e.g.,
            an adapter bolt that has an ISO thread and an UTC tapped hole).
            To avoid any loss of precision, we return the size in the unit
            that was indicated on the drawing.

        size_tolerance: Tolerance details. Default: General tolerances.
            By default we are referring to the general tolerances of the drawing.
            When you are also requesting the TitleBlock, we are attaching the
            applicable General Tolerances (assuming they were understood)
            to the measure. This will consider the nominal size of the
            measure.
            If the W24MeasureLabel describes a "Theoretically Exact Measure",
            i.e, the label is surrounded by a box, like: "[15]", the size_tolerance
            refers to a W24ToleranceTheoreticallyExact object (and is NOT None)

        unit: Length unit of the size. This information is only available
            when you request the TitleBlock as well; as only the title block
            will allow us to determine the geographic origin of the drawing.

        thread: Optional thread details.
            The thread details describe the complete thread description
            and follow the respective standards. In consequence, the thread
            diameter of an ISO-thread will be indicated in millimeter,
            while the thread diameter of an UTS thread will be in inch.

        chamfer: Optional Chamfer

        depth: Depth of the drilling or thread. Uses the same dimensions

        counterbore: Counterbore details. This is usually defined for holes
            threads.

        countersink: Countersink details. This is usually defined for holes
            threads.

        counterdrill: Counterdrill details. This is usually defined for holes
            threads.

    """

    @field_validator("size_tolerance", mode="before")
    def deserialize_size_tolerance(cls, v):
        if isinstance(v, W24Tolerance):
            return v
        return W24Tolerance.parse_obj(v)

    blurb: str

    quantity: int = 1

    size: W24Size

    size_tolerance: W24ToleranceType = W24ToleranceGeneral()

    unit: Optional[W24UnitLength] = None

    secondary_unit: Optional[W24UnitLength] = Field(
        None,
        description=(
            "Secondary unit of measurement. For measures like 1.000 [25.40], "
            "the unit will be inch and the secondary_unit would be millimeter."
        ),
    )

    thread: Optional[W24ThreadUnion] = None

    chamfer: Optional[W24Chamfer] = None

    depth: Optional[W24Depth] = None

    test_dimension: Optional[W24TestDimension] = None

    counterbores: List[W24CounterBore] = []

    countersinks: List[W24CounterSink] = []

    counterdrills: List[W24CounterDrill] = []


class W24Measure(W24BaseFeatureModel):
    """Measure object

    Attributes:

        measure_id: Unique UUID4 identifier

        label: Measure Label

        warnings: List of Warnings that are associated with the
            measure. See W24MeasureWarning for details.

        confidence:  Werk24 calculates an internal confidence score for
            each measure. Depending on your use-case, you might want
            to consider or discard low-confidence measures. This
            value allows you to do so. The value ranges from
            0.0 to 1.0

    """

    measure_id: Optional[UUID4] = None

    label: W24MeasureLabel

    warnings: List[W24MeasureWarning] = []

    confidence: float = 0.0
