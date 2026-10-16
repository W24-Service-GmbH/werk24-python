"""A client older than the API keeps the fields it does not know, and says so.

New fields reach the API before they reach every installed copy of this
library. Parsed the default way, pydantic drops the fields a model does not
declare, so such a client got an answer with fields missing and nothing to
tell it. ``TechreadMessage`` now parses a v2 answer with those fields kept on
the model (``model_extra``) and logs one warning per field naming it.

The models' own configuration is unchanged: constructed directly they still
drop unknown fields, and ``model_dump()`` still leaves kept ones out, so
nothing changes for code that builds responses from these models.

The other way an answer used to change shape silently is a value this
version cannot accept, such as a new enum member: the whole answer stays the
plain dict the server sent. That still happens, but it is logged too.
"""

import json
import logging
import uuid
from decimal import Decimal

import pytest

from werk24 import (
    ResponseFeaturesComponentDrawing,
    Size,
    SizeType,
    Slot,
    TechreadMessage,
)
from werk24.models.v2 import internal


@pytest.fixture(autouse=True)
def _fresh_reports(monkeypatch):
    """Each test starts with nothing reported yet."""
    monkeypatch.setattr(internal, "_REPORTED_UNKNOWN_FIELDS", set())
    monkeypatch.setattr(internal, "_REPORTED_UNPARSED", set())


def _mm(value: str) -> Size:
    return Size(
        size_type=SizeType.LINEAR, value=Decimal(value), tolerance=None, unit="millimeter"
    )


def _features_payload(**extra) -> dict:
    """A features answer as the server sends it, with ``extra`` merged in."""
    response = ResponseFeaturesComponentDrawing(
        slots=[
            Slot(
                reference_id=1,
                label="2x Slot 14x15",
                confidence=None,
                quantity=2,
                width=_mm("14"),
                length=_mm("15"),
            )
        ]
    )
    payload = json.loads(response.model_dump_json())
    payload.update(extra)
    return payload


def _message(payload: dict) -> TechreadMessage:
    return TechreadMessage.model_validate_json(
        json.dumps(
            {
                "request_id": str(uuid.uuid4()),
                "message_type": "ASK",
                "message_subtype": "FEATURES",
                "page_number": 0,
                "payload_dict": payload,
            }
        )
    )


def _warnings(caplog) -> list:
    return [
        r.getMessage()
        for r in caplog.records
        if r.name == "werk24" and r.levelno == logging.WARNING
    ]


def test_a_known_answer_parses_as_before_and_warns_nothing(caplog):
    caplog.set_level(logging.WARNING, logger="werk24")

    message = _message(_features_payload())

    assert isinstance(message.payload_dict, ResponseFeaturesComponentDrawing)
    assert message.payload_dict.model_extra == {}
    assert message.payload_dict.slots[0].width.value == Decimal("14")
    assert _warnings(caplog) == []


def test_an_unknown_top_level_field_is_kept_on_the_response(caplog):
    caplog.set_level(logging.WARNING, logger="werk24")
    grooves = [{"reference_id": 2, "label": "1x Groove 3x1"}]

    message = _message(_features_payload(o_ring_grooves=grooves))

    response = message.payload_dict
    assert isinstance(response, ResponseFeaturesComponentDrawing)
    assert response.o_ring_grooves == grooves
    assert response.model_extra == {"o_ring_grooves": grooves}
    # The known fields are still typed.
    assert isinstance(response.slots[0], Slot)


def test_an_unknown_nested_field_is_kept_on_its_item(caplog):
    caplog.set_level(logging.WARNING, logger="werk24")
    payload = _features_payload()
    payload["slots"][0]["orientation"] = "HORIZONTAL"

    slot = _message(payload).payload_dict.slots[0]

    assert slot.orientation == "HORIZONTAL"
    assert internal._unknown_fields(_message(payload).payload_dict) == [
        "slots[].orientation"
    ]


def test_each_unknown_field_is_named_once_with_the_upgrade_line(caplog):
    caplog.set_level(logging.WARNING, logger="werk24")
    payload = _features_payload(o_ring_grooves=[])
    payload["slots"][0]["orientation"] = "HORIZONTAL"

    _message(payload)
    _message(payload)

    warnings = _warnings(caplog)
    assert len(warnings) == 1
    assert "o_ring_grooves" in warnings[0]
    assert "slots[].orientation" in warnings[0]
    assert "ResponseFeaturesComponentDrawing" in warnings[0]
    assert "pip install -U werk24" in warnings[0]


def test_a_field_seen_later_gets_its_own_warning(caplog):
    caplog.set_level(logging.WARNING, logger="werk24")

    _message(_features_payload(o_ring_grooves=[]))
    _message(_features_payload(o_ring_grooves=[], knurls=[]))

    warnings = _warnings(caplog)
    assert len(warnings) == 2
    assert "knurls" in warnings[1]
    assert "o_ring_grooves" not in warnings[1]


def test_kept_fields_do_not_change_what_the_models_serialize():
    """Building or dumping a response behaves exactly as before."""
    built = ResponseFeaturesComponentDrawing(o_ring_grooves=[])
    assert built.model_extra is None or built.model_extra == {}
    assert "o_ring_grooves" not in built.model_dump()

    parsed = _message(_features_payload(o_ring_grooves=[])).payload_dict
    assert "o_ring_grooves" not in parsed.model_dump()
    assert "o_ring_grooves" not in parsed.model_dump_json()


def test_an_answer_that_cannot_be_read_stays_a_dict_and_says_why(caplog):
    caplog.set_level(logging.WARNING, logger="werk24")
    payload = _features_payload(
        fasteners=[
            {
                "reference_id": 3,
                "label": "4x Rivet",
                "confidence": None,
                "fastener_type": "SOME_FUTURE_TYPE",
                "quantity": 4,
            }
        ]
    )

    message = _message(payload)
    _message(payload)

    assert isinstance(message.payload_dict, dict)
    assert message.payload_dict["fasteners"][0]["fastener_type"] == "SOME_FUTURE_TYPE"
    warnings = _warnings(caplog)
    assert len(warnings) == 1
    assert "ResponseFeaturesComponentDrawing" in warnings[0]
    assert "fasteners.0.fastener_type" in warnings[0]
    assert "payload_dict is the plain dict" in warnings[0]
