from decimal import Decimal
from typing import Any, Dict, List, Optional, Type, Union

from pydantic import BaseModel, field_validator

from .gender import W24Gender
from .thread import (
    W24Thread,
    W24ThreadACME,
    W24ThreadISOMetric,
    W24ThreadKnuckle,
    W24ThreadNPT,
    W24ThreadSM,
    W24ThreadUTS,
    W24ThreadWhitworth,
)


def deserialize_thread(
    raw: Union[Dict[str, Any], W24Thread],
) -> W24Thread:
    """Deserialize a specific ask in its raw form

    Args:
        raw (Dict[str, Any]): Raw Ask as it arrives from the
            json deserializer

    Returns:
        W24AskUnion: Corresponding ask type
    """
    if isinstance(raw, dict):
        ask_type = _deserialize_thread_type(raw.get("thread_type", ""))
        return ask_type.parse_obj(raw)

    if isinstance(raw, W24Thread):
        return raw

    raise ValueError(f"Unsupported value type '{type(raw)}'")


def _deserialize_thread_type(ask_type: str) -> Type[W24Thread]:
    """Get the Ask Class from the ask type

    Args:
        ask_type (str): Ask type in question

    Raises:
        ValueError: Raised if ask type is unknown

    Returns:
        str: Name of the AskObject
    """
    class_ = {
        "ACME": W24ThreadACME,
        "ISO_METRIC": W24ThreadISOMetric,
        "NPT": W24ThreadNPT,
        "SM": W24ThreadSM,
        "WHITWORTH": W24ThreadWhitworth,
        "UTS": W24ThreadUTS,
        "KNUCKLE": W24ThreadKnuckle,
    }.get(ask_type, None)

    if class_ is None:
        raise ValueError(f"Unknown Ask Type '{ask_type}'")

    return class_


class W24ThreadElement(BaseModel):
    """Characterization of a Thread Element

    Attributes:
        quantity (int): Number of equivalent elements that are
            indicated by one label (e.g., 3xM5).

        gender (Optional[W24Gender]): Gender (male or female) of the thread feature.
            This is determined by checking whether the thread is
            located on the outer contour of the part or inside the part.
            When the outer contour is unavailable (e.g., in detail drawings),
            the gender is set to None.

        length (Optional[Decimal]): Length of the stud corresponding
            to the thread. Please keep in mind that a thus can
            contain multiple threads with different lengths. This
            is considered in the threads themselves.
            NOTE: we are using the word length here to differentiate
            it from the thread depth which describes the difference
            between the major and minor radii.

        threads (List[W24Thread]): List of Threads that are positioned
            on the ThreadElements. This is a list to support multi-threads
    """

    quantity: int

    gender: Optional[W24Gender]

    length: Optional[Decimal]

    threads: List[W24Thread]

    @field_validator("threads", mode="before")
    def ask_list_validator(cls, raw: List[Dict[str, Any]]) -> List[W24Thread]:
        """Validator to de-serialize the asks. The de-serialization
        is based on the ask_type attribute of the object. Pydantic
        does not support this out-of-the box

        Args:
            raw (Dict[str, Any]): Raw json of the asks list

        Returns:
            List[W24AskUnion]: List of deserialized Asks
        """
        return [deserialize_thread(t) for t in raw]
