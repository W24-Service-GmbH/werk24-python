from enum import Enum


class W24Alphabet(str, Enum):
    """List of Alphabets

    This lists all alphabets that the Werk24 API
    can differentiate. If you are processing
    Technical Drawings in another alphabet, please
    give us a call.

    Additional Alphabets include:
    * Armenian
    * Canadian Syllabic
    * Ethiopic
    * Georgian
    * North Indic
    * Sough Indic
    * Thaana

    """

    ARABIC = "ARABIC"
    CJK = "CJK"
    CYRILLIC = "CYRILLIC"
    GREEK = "GREEK"
    HANGUL = "HANGUL"
    HEBREW = "HEBREW"
    HIRAGANA = "HIRAGANA"
    KATAKANA = "KATAKANA"
    LATIN = "LATIN"
    THAI = "THAI"
