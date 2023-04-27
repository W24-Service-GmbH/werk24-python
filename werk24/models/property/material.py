from typing import Literal

from werk24.models.property.base import W24Property
from werk24.models.material import W24Material
from typing import List


class W24PropertyMaterial(W24Property):
    """Material Property of the Material.

    Keep in mind that a part can be manufactured from
    multiple materials (e.g., using 2 different Polymers),
    or specify alternative materials.

    NOTE: future implementations will contain
        more information regarding the shape of
        the input material.

    Attributes:
        materials: Nested List of the materials.
            First layer allows AND-connections,
            the second layer OR-connections.
            This way we are able to encode the
            material specification like these:
            MAT1 and (MAT2 or MAT3) - which occurs
            sometimes for polymer-based part.
            The result would be [[MAT1],[MAT2,MAT3]].
    """
    property_type: Literal["MATERIAL"] = "MATERIAL"
    property_subtype: Literal["MATERIAL"] = "MATERIAL"
    materials: List[List[W24Material]]
