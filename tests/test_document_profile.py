"""Tests for the document profile ask and response.

The profile answers two questions before any interpretation begins: what kind
of document this is, and how long it is likely to take. Both are useful only
if they arrive early and are honest about what they do not know, which is what
these tests pin.
"""

import pytest
from pydantic import ValidationError

from werk24.models.v2.asks import AskDocumentProfile, get_ask_subclasses
from werk24.models.v2.enums import AskType, PageType
from werk24.models.v2.models import ProcessingTimeEstimate
from werk24.models.v2.responses import (
    RESPONSE_SUBCLASSES,
    ResponseDocumentProfile,
)


class TestRegistration:
    def test_the_ask_registers_itself(self):
        # AskUnion is derived from __subclasses__, so a new ask that is never
        # imported is a new ask the server can never be sent.
        assert AskDocumentProfile in get_ask_subclasses()

    def test_the_response_registers_itself(self):
        assert ResponseDocumentProfile in RESPONSE_SUBCLASSES

    def test_the_ask_type_round_trips(self):
        ask = AskDocumentProfile()
        assert ask.ask_type == AskType.DOCUMENT_PROFILE
        assert AskDocumentProfile.model_validate_json(ask.model_dump_json()) == ask


class TestProcessingTimeEstimate:
    def test_it_carries_a_range_not_a_point(self):
        # Werk24's processing time has a long right tail: the median is around
        # half a minute and the 99th percentile is over two. A single number
        # would be wrong in the only case where being wrong costs anything —
        # the request you are still waiting on.
        estimate = ProcessingTimeEstimate(seconds_p50=21.1, seconds_p95=60.0)
        assert estimate.seconds_p50 < estimate.seconds_p95

    def test_both_percentiles_are_required(self):
        with pytest.raises(ValidationError):
            ProcessingTimeEstimate(seconds_p50=21.1)


class TestResponse:
    def test_a_minimal_response_needs_only_the_page_count(self):
        # Everything else is genuinely optional: a raster states no paper size,
        # and an unusual shape may have no estimate.
        response = ResponseDocumentProfile(page_count=1)
        assert response.page_count == 1
        assert response.paper_size is None
        assert response.processing_time is None

    def test_an_unclassified_page_is_miscellaneous_not_a_component_drawing(self):
        # The important default. Every other response in this API hardcodes
        # `Literal[PageType.COMPONENT_DRAWING]`, so defaulting to it here would
        # assert something we did not determine.
        assert ResponseDocumentProfile(page_count=1).page_type is PageType.MISCELLANEOUS

    def test_it_can_name_a_document_we_do_not_interpret(self):
        # The whole point of the extra members: telling a caller their P&ID is
        # a P&ID is a better answer than an empty component drawing.
        response = ResponseDocumentProfile(
            page_count=1, page_type=PageType.PID_DRAWING
        )
        assert response.page_type is PageType.PID_DRAWING

    def test_a_raster_has_no_paper_size_rather_than_a_guessed_one(self):
        response = ResponseDocumentProfile(page_count=1, paper_size=None)
        assert response.paper_size is None

    def test_it_round_trips_through_json(self):
        response = ResponseDocumentProfile(
            page_count=3,
            page_type=PageType.ASSEMBLY_DRAWING,
            paper_size="ANSI_D",
            processing_time=ProcessingTimeEstimate(seconds_p50=34.9, seconds_p95=120.0),
        )
        restored = ResponseDocumentProfile.model_validate_json(
            response.model_dump_json()
        )
        assert restored == response
        assert restored.processing_time.seconds_p95 == 120.0


class TestPageType:
    def test_the_interpreted_and_recognised_types_are_both_present(self):
        values = {member.value for member in PageType}
        assert {"COMPONENT_DRAWING", "ASSEMBLY_DRAWING"} <= values
        assert {"ARCHITECTURAL_DRAWING", "PID_DRAWING", "WIRING_DIAGRAM"} <= values
        assert "MISCELLANEOUS" in values

    def test_the_electrical_document_is_named_for_itself(self):
        # WIRING_DIAGRAM, not WIRE_DRAWING: the latter is a metal-forming
        # process and would collide with a manufacturing term.
        assert PageType.WIRING_DIAGRAM.value == "WIRING_DIAGRAM"

    def test_existing_responses_still_pin_component_drawing(self):
        # Adding members must not loosen the responses that already declare
        # `Literal[PageType.COMPONENT_DRAWING]`.
        from werk24.models.v2.responses import ResponseMetaDataComponentDrawing

        with pytest.raises(ValidationError):
            ResponseMetaDataComponentDrawing(page_type=PageType.PID_DRAWING)
