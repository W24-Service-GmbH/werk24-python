from pydantic import BaseModel, Field
from pydantic_extra_types.color import Color
from werk24.models.alphabet import W24Alphabet


class W24Font(BaseModel):
    """Font Specification.

    Allows you to specify which font shall be used.

    """

    font_family: str = Field(
        description="Font Family",
    )
    font_style: str = Field(
        description="Font Style",
        examples=["Regular", "Medium"],
        default="Regular",
    )
    font_size: float = Field(
        description="Font Size in pt.",
        examples=[10, 15],
    )
    font_color: Color = Field(
        description="Font Color",
        default=Color((0, 0, 0)),
    )


class W24FontMap(BaseModel):
    """Object that maps alphabets to fonts.

    This allows you to support multiple alphabets
    e.g., one for Latin characters and one for
    Chinese Hanzi. Be aware that the font selection
    is performed word-by-word.

    NOTE: you always need to specify a Latin script,
    as decimals are considered to be part of the Latin
    script. (Courtesy of!? the developers of the Brahmi script).
    See: https://en.wikipedia.org/wiki/Brahmi_numerals
    """

    font_map: dict[W24Alphabet, W24Font] = Field(
        description="Dictionary that maps an alphabet to a font",
        examples={W24Alphabet.LATIN: W24Font(font_family="Work Sans", font_size=10)},
    )
