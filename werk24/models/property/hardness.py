from enum import Enum
from typing import Literal, Optional

from werk24.models.property.base import W24Property
from werk24.models.value import W24PhysicalQuantity, W24Value, W24ValueRange


class W24PropertyHardnessRockwellScale(str, Enum):
    A = "A"
    B = "BW"
    C = "C"
    D = "D"
    E = "EW"
    F = "FW"
    G = "GW"
    H = "HW"
    K = "KW"
    _15N = "15N"
    _30N = "30N"
    _45N = "45N"
    _15T = "15TW"
    _30T = "30TW"
    _45T = "45TW"


class W24PropertyHardnessRockwell(W24Property):
    type: Literal["HARDNESS_ROCKWELL"] = "HARDNESS_ROCKWELL"
    hardness_number_range: W24ValueRange
    hardness_scale: W24PropertyHardnessRockwellScale
    """
    Quote from EN ISO 6508-1:2006 page 9:
        "The Sm in the scale designations indicates that
        a steel ball indenter and a diamond spot specimen
        holder are used for this testing.
    """
    use_sm_indenter_and_holder: bool = False


class W24PropertyHardnessLeebScale(str, Enum):
    D = "D"
    DL = "DL"
    D_PLUS_15 = "D+15"
    S = "S"
    E = "E"
    G = "G"
    C = "C"


class W24PropertyHardnessLeeb(W24Property):
    type: Literal["HARDNESS_LEEB"] = "HARDNESS_LEEB"
    hardness_number_range: W24ValueRange
    hardness_scale: W24PropertyHardnessLeebScale


class W24PropertyHardnessVickers(W24Property):
    type: Literal["HARDNESS_VICKERS"] = "HARDNESS_VICKERS"
    hardness_number_range: W24ValueRange
    load: Optional[W24Value]
    loading_time: Optional[W24Value]


class W24PropertyHardnessBrinell(W24Property):
    type: Literal["HARDNESS_BRINELL"] = "HARDNESS_BRINELL"
    hardness_number_range: W24ValueRange
    ball_diameter: Optional[W24PhysicalQuantity]
    load: Optional[W24PhysicalQuantity]
    loading_time: Optional[W24PhysicalQuantity]


class W24PropertyHardnessKnoop(W24Property):
    type: Literal["HARDNESS_KNOOP"] = "HARDNESS_KNOOP"
    hardness_number_range: W24ValueRange
    test_duration: Optional[W24PhysicalQuantity]
    test_force: Optional[W24PhysicalQuantity]
