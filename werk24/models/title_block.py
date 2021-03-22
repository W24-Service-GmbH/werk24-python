from typing import List, Optional

from pydantic import BaseModel

from .general_tolerances import W24GeneralTolerances
from .language import W24Language
from .material import W24Material


class W24TitleBlockLabel:

    blurb: str
    """ Blurb for human consumption
    """

    language: W24Language
    """ Language in accordance with the ISO/639-2B norm
    """

    text: str
    """ Text of the identification
    """


class W24TitelBlockId:

    blurb: str
    """ name: value pair for human consumpation
    """

    names: List[W24TitleBlockLabel]
    """ List of indentification names in different languages
    """

    value: str
    """ Value of the identification number
    """


class W24TitleBlockDesignation(BaseModel):
    """ Representation of the Designation
    """

    names: List[W24TitleBlockLabel]
    """ List of indentification names in different languages
    """

    value: str
    """ Value of the identification number
    """


class W24TitelBlock(BaseModel):
    """ Information that could be extracted from the
    Title Block
    """

    designation: Optional[W24TitleBlockDesignation]
    """ Designation of the Sheet on the Title Block
    """

    drawing_id: Optional[W24TitelBlockId]
    """ Main Identification Number of the Drawing
    """

    general_tolerances: Optional[W24GeneralTolerances]
    """ General Tolerances quoted on the TitleBlock
    """

    internal_ids: List[W24TitelBlockId]
    """ List of additional identificatoin numbers
    detected on the Drawing
    """

    material: Optional[W24Material]
    """ Material which is quoted on the TitleBlock
    """


