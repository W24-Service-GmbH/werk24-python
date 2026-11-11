"""Redacting areas the caller chose, and mapping a sheet image onto its page."""

import pytest
from pydantic import ValidationError

from werk24 import (
    AskRedaction,
    PageTransform,
    RedactionArea,
    ResponseRedaction,
    TechreadMessage,
)


def _area(**overrides):
    values = {"page_index": 0, "x0": 10.0, "y0": 20.0, "x1": 110.0, "y1": 60.0}
    values.update(overrides)
    return RedactionArea(**values)


def test_an_area_needs_width_and_height():
    with pytest.raises(ValidationError):
        _area(x1=10.0)
    with pytest.raises(ValidationError):
        _area(y1=5.0)


def test_an_area_names_a_page_from_zero():
    with pytest.raises(ValidationError):
        _area(page_index=-1)


def test_an_ask_without_areas_is_unchanged():
    ask = AskRedaction()
    assert ask.redaction_areas is None
    assert ask.fill_color == "#ffffff"


def test_areas_need_a_fill_colour():
    with pytest.raises(ValidationError, match="fill_color"):
        AskRedaction(fill_color=None, redaction_areas=[_area()])


def test_areas_need_pdf_output():
    with pytest.raises(ValidationError, match="output_format"):
        AskRedaction(output_format="PNG", redaction_areas=[_area()])


def test_an_empty_list_of_areas_is_allowed():
    # Nothing to remove, but the file still goes through the redaction
    # (metadata, comments and the like): a person may have removed every zone.
    assert AskRedaction(redaction_areas=[]).redaction_areas == []


def test_areas_survive_the_round_trip():
    ask = AskRedaction(fill_color="#000000", redaction_areas=[_area(page_index=1)])
    again = AskRedaction.model_validate_json(ask.model_dump_json())
    assert again.redaction_areas == ask.redaction_areas


def test_a_response_carries_the_page_transform():
    transform = PageTransform(
        page_index=2,
        page_width=1190.55,
        page_height=841.89,
        matrix=(0.36, 0.0, 0.0, 0.36, 1.5, -2.0),
    )
    response = ResponseRedaction(page_transform=transform)
    again = ResponseRedaction.model_validate_json(response.model_dump_json())
    assert again.page_transform == transform


def test_a_response_from_an_older_server_has_no_transform():
    response = ResponseRedaction.model_validate({"redaction_zones": []})
    assert response.page_transform is None


def test_the_transform_reaches_a_message_payload():
    message = TechreadMessage.model_validate(
        {
            "request_id": "3f2b8c1e-4d5a-4b6c-9e7f-1a2b3c4d5e6f",
            "message_type": "ASK",
            "message_subtype": "REDACTION",
            "page_number": 0,
            "payload_dict": {
                "ask_type": "REDACTION",
                "redaction_zones": [],
                "page_transform": {
                    "page_index": 0,
                    "page_width": 595.0,
                    "page_height": 842.0,
                    "matrix": [0.36, 0, 0, 0.36, 0, 0],
                },
            },
        }
    )
    payload = message.payload_dict
    if isinstance(payload, dict):
        payload = ResponseRedaction.model_validate(payload)
    assert payload.page_transform.matrix == (0.36, 0.0, 0.0, 0.36, 0.0, 0.0)
