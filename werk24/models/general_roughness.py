from typing import List

from .base_feature import W24BaseFeatureModel
from .roughness import W24RoughnessLabel


class W24GeneralRoughnessReference(W24BaseFeatureModel):
    """ General Roughness Reference

    Attributes:
    ----------
        roughness_label: Simplified reference indication
            used to save space or for simplification purpose.

        roughness_label_value: Meaning of the roughness_label, 
            explaining what surface roughness is applicable 
            when the roughness_label is specified on a 
            workpiece.  

    """
    reference_indication_label: str
    reference_indication_value: W24RoughnessLabel


class W24GeneralRoughness(W24BaseFeatureModel):
    """ General Roughness object

    Attributes:
    ----------
        general_roughness: Surface Roughness Specification 
            required for all surfaces of a workpiece. Unless 
            any deviation is specified. 

        deviating_roughnesses: Indicates deviations from 
            the general surface roughness requirements.

        roughness_references: A Simplified reference indication
            used to save space or for simplification purpose, 
            provided the meaning of this reference symbol 
            is specified somewhere on the drawing.  
    """

    general_roughness: List[W24RoughnessLabel]
    deviating_roughnesses: List[W24RoughnessLabel]
