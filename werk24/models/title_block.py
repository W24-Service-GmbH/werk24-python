from typing import List, Optional

from pydantic import BaseModel

from .general_tolerances import W24GeneralTolerances
from .language import W24Language
from .material import W24Material


class W24TitleBlockCaption(BaseModel):
    """ Per-Language caption that was chosed to represent the caption-value pair.

    Attributes:
        language: Language in accordance with the ISO/639-2B norm

        text: Text of the identification
    """

    language: Optional[W24Language]

    text: str


class W24CaptionValuePair(BaseModel):
    """ Caption-Value pair for that were found on the Title Block.

    Attributes:
        blurb: Caption-Value pair for human consumption

        captions: List of captions in different languages.
            This will only return the languages that were detected and
            NOT translate the captions into languages that are not present
            on the drawing. This behavior might however change in the
            future.
    """
    blurb: str

    captions: List[W24TitleBlockCaption]

    value: str


class W24TitleBlock(BaseModel):
    """ Information that could be extracted from the
    Title Block

    Attributes:
        designation: Designation of the Sheet on the Title Block

        drawing_id: Main Identification Number of the Drawing

        reference_ids: List of additional reference IDs
            detected on the Drawing

        general_tolerances: General Tolerances quoted on the TitleBlock

        material: Material which is quoted on the TitleBlock

    """

    designation: Optional[W24CaptionValuePair]

    drawing_id: Optional[W24CaptionValuePair]

    reference_ids: List[W24CaptionValuePair]

    general_tolerances: Optional[W24GeneralTolerances]

    material: Optional[W24Material]
