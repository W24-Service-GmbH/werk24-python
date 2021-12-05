from typing import Any, Dict, List, Optional

from pydantic import BaseModel, validator

from .general_tolerances import W24GeneralTolerances
from .language import W24Language
from .material import W24Material
from .weight import W24Weight


class W24TitleBlockItem(BaseModel):
    """ Per-Language caption or value

    Attributes:
        language: Language in accordance with the ISO/639-2B standards

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

    captions: List[W24TitleBlockItem]

    values: List[W24TitleBlockItem]


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

        weight: Weight as read from the TitleBlock. NOTE: this is not
            cross-checked with the material and volume of the part,
            but provided as it was read on the TitleBlock.

    """

    designation: Optional[W24CaptionValuePair]

    drawing_id: Optional[W24CaptionValuePair]

    reference_ids: List[W24CaptionValuePair]

    general_tolerances: Optional[W24GeneralTolerances]

    material: Optional[W24Material]

    weight: Optional[W24Weight]

    @validator('designation', pre=True)
    def designation_validator(
        cls,
        raw: Dict[str, Any]
    ) -> Optional[W24CaptionValuePair]:
        """ Workaround to deal with the transition period
        while we move from the single-value to the multi-value
        pairs.

        This code can be removed after we complete the
        transition.

        Args:
            raw (Dict[str, Any]): Unparsed value returned
                from the API

        Returns:
            W24CaptionValuePair: Parse value-caption pair
        """
        return cls._parse_caption_value_pair(raw)

    @validator('drawing_id', pre=True)
    def drawing_id_validator(
        cls,
        raw: Dict[str, Any]
    ) -> Optional[W24CaptionValuePair]:
        """ Workaround to deal with the transition period
        while we move from the single-value to the multi-value
        pairs.

        This code can be removed after we complete the
        transition.

        Args:
            raw (Dict[str, Any]): Unparsed value returned
                from the API

        Returns:
            W24CaptionValuePair: Parse value-caption pair
        """
        return cls._parse_caption_value_pair(raw)

    @validator('reference_ids', pre=True)
    def reference_ids_validator(
        cls,
        raw: List[Dict[str, Any]]
    ) -> List[W24CaptionValuePair]:
        """ Workaround to deal with the transition period
        while we move from the single-value to the multi-value
        pairs.

        This code can be removed after we complete the
        transition.

        Args:
            raw (List[Dict[str, Any]]): Unparsed value returned
                from the API

        Returns:
            List[W24CaptionValuePair]: Parse value-caption pair
        """
        result = [
            cls._parse_caption_value_pair(e)
            for e in raw
        ]
        return [r for r in result if r is not None]

    @staticmethod
    def _parse_caption_value_pair(
        raw: Optional[Dict[str, Any]]
    ) -> Optional[W24CaptionValuePair]:
        """ Workaround to deal with the transition period
        while we move from the single-value to the multi-value
        pairs.

        This code can be removed after we complete the
        transition.

        Args:
            raw (Dict[str, Any]): Unparsed value returned
                from the API

        Returns:
            W24CaptionValuePair: Parse value-caption pair
        """
        if isinstance(raw, W24CaptionValuePair):
            return raw

        if raw is None:
            return None

        if 'value' in raw.keys():
            raw['values'] = [{
                'language': None,
                'text': raw.get('value')
            }]
            del raw['value']

        return W24CaptionValuePair.parse_obj(raw)
