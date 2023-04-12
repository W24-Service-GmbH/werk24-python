from enum import Enum
from typing import Literal, Optional

from werk24.models.property.base import W24Property
from werk24.models.value import W24PhysicalQuantity, W24Value


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


class W24PropertyHardness(W24Property):
    property_type: Literal["HARDNESS"] = "HARDNESS"


class W24PropertyHardnessRockwell(W24PropertyHardness):
    """Rockwell Hardness.

    Attributes:
        hardness_number (W24Value): Specified hardness
             number. This might be a range.

        hardness_scale (W24PropertyHardnessRockwellScale):
            Rockwell hardness scale.

        use_sm_indenter_and_holder (bool): Quote from
            EN ISO 6508-1:2006 page 9:
            "The Sm in the scale designations indicates that
            a steel ball indenter and a diamond spot specimen
            holder are used for this testing.
    """
    property_subtype: Literal["ROCKWELL"] = "ROCKWELL"
    hardness_number: W24Value
    hardness_scale: W24PropertyHardnessRockwellScale
    use_sm_indenter_and_holder: bool = False


class W24PropertyHardnessRockwellScale(str, Enum):
    """List of available Rockwell hardness scales.
    """
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


class W24PropertyHardnessLeebScale(str, Enum):
    """List of available Leeb hardness scales.
    """
    D = "D"
    DL = "DL"
    D_PLUS_15 = "D+15"
    S = "S"
    E = "E"
    G = "G"
    C = "C"


class W24PropertyHardnessLeeb(W24PropertyHardness):
    """Leeb Hardness.

    Attributes:
        hardness_number (W24Value): Specified hardness
             number. This might be a range.

        hardness_scale (W24PropertyHardnessLeebScale):
            Leeb hardness scale.
    """
    property_subtype: Literal["LEEB"] = "LEEB"
    hardness_number: W24Value
    hardness_scale: W24PropertyHardnessLeebScale


class W24PropertyHardnessVickers(W24PropertyHardness):
    """Vickers Hardness.

    Attributes:
        hardness_number (W24Value): Specified hardness
             number. This might be a range.

        load (W24PhysicalQuantity): Load for the Vickers
            hardness test. Typically indicated in kgf.

        lading_time (W24PhysicalQuantity): Loading time for
            the Vickers hardness test. Typically indicated
            in seconds.
    """
    property_subtype: Literal["VICKERS"] = "VICKERS"
    hardness_number: W24Value
    load: Optional[W24PhysicalQuantity]
    loading_time: Optional[W24PhysicalQuantity]


class W24PropertyHardnessBrinell(W24PropertyHardness):
    """Brinell Hardness.

    Attributes:
        hardness_number (W24Value): Specified hardness
             number. This might be a range.

        ball_diameter (W24PhysicalQuantity): Ball diameter
            for the Brinell test. Typically indicated in
            mm.

        load (W24PhysicalQuantity): Load for the Brinell
            hardness test. Typically indicated in kgf.

        lading_time (W24PhysicalQuantity): Loading time for
            the v hardness test. Typically indicated
            in seconds.
    """
    property_subtype: Literal["BRINELL"] = "BRINELL"
    hardness_number: W24Value
    ball_diameter: Optional[W24PhysicalQuantity]
    load: Optional[W24PhysicalQuantity]
    loading_time: Optional[W24PhysicalQuantity]


class W24PropertyHardnessKnoop(W24PropertyHardness):
    """Knoop Hardness.

    Attributes:
        hardness_number (W24Value): Specified hardness
             number. This might be a range.


        test_duration (W24PhysicalQuantity): Duration of
            the test. Typically indicated in seconds.

        test_force (W24PhysicalQuantity): Force applied
            during the test. Typically indicated in kgf.
    """
    property_subtype: Literal["KNOOP"] = "KNOOP"
    hardness_number: W24Value
    test_duration: Optional[W24PhysicalQuantity]
    test_force: Optional[W24PhysicalQuantity]
