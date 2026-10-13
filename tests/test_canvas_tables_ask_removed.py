"""The CANVAS_TABLES ask is no longer part of the models.

The API never returned a result for it, so the client no longer offers it.
An ask list that still names it is refused when it is built, in either
generation's union and by the v1 deserializer, instead of being sent and
left without an answer.
"""

import pytest
from pydantic import TypeAdapter, ValidationError

import werk24.models.v1.ask as v1_ask
from werk24 import AskUnion
from werk24.models.v1.ask import W24AskType, W24AskUnion, deserialize_ask_v1


def test_the_ask_type_and_its_model_are_gone():
    assert "CANVAS_TABLES" not in W24AskType.__members__
    assert not hasattr(v1_ask, "W24AskCanvasTables")


@pytest.mark.parametrize(
    "adapter",
    [TypeAdapter(list[AskUnion]), TypeAdapter(list[W24AskUnion])],
    ids=["AskUnion", "W24AskUnion"],
)
def test_an_ask_list_naming_it_is_refused(adapter):
    with pytest.raises(ValidationError):
        adapter.validate_python([{"ask_type": "NOTES"}, {"ask_type": "CANVAS_TABLES"}])


def test_the_v1_deserializer_refuses_it():
    with pytest.raises(ValueError, match="Unknown Ask Type"):
        deserialize_ask_v1({"ask_type": "CANVAS_TABLES"})


def test_the_asks_next_to_it_still_resolve():
    asks = TypeAdapter(list[AskUnion]).validate_python(
        [{"ask_type": "NOTES"}, {"ask_type": "EXCEL_SUMMARY"}]
    )
    assert [type(ask).__name__ for ask in asks] == [
        "W24AskNotes",
        "W24AskExcelSummary",
    ]
