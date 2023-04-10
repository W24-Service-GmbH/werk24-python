""" Data Model for Canvas and Sectional Notes.

Author: Jochen Mattes
"""
from enum import Enum

from werk24.models.base_feature import W24BaseFeatureModel


class W24NoteType(str, Enum):
    """Differentiation between Canvas and Sectional Notes.

    Canvas Notes are sometimes referred to as "General Notes",
    they are associated with the canvas in general.

    Sectional Notes are associated with a specific sectional,
    but not as part of a leader or call-out. (e.g., "VIEW A")

    Sectional Call Outs are linked to the sectional through
    a leader symbol (e.g., "MARK HERE")

    NOTE: please note that we are only returning the information
    that is not understood by the system through another way.
    Over time, number of sectional call outs will thus gradually
    reduce.
    """
    CANVAS_NOTE = "CANVAS NOTE"
    SECTIONAL_NOTE = "SECTIONAL NOTE"
    SECTIONAL_CALLOUT = "SECTIONAL_CALLOUT"


class W24Note(W24BaseFeatureModel):
    """Notes object for Sectional and Canvas Notes.

    Attributes:
        type (W24NoteType): Type of the note to differentiate
            between notes that are associated with the complete
            sectional and the canvas

        text (str): Raw text that was read.
    """
    type: W24NoteType
    text: str
