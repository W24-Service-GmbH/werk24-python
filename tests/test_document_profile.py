"""Tests for the document profile ask and response.

The profile answers two questions before any interpretation begins: what kind
of document this is, and how long it is likely to take. Both are useful only
if they arrive early and are honest about what they do not know, which is what
these tests pin.
"""

import pytest
from pydantic import ValidationError

from werk24.models.v2.asks import AskDocumentProfile, get_ask_subclasses
from werk24.models.v2.enums import AskType, PageType, PaperSize
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

    def test_an_unnamed_sheet_is_custom_which_is_not_the_same_as_none(self):
        # Two different facts that a single Optional would conflate: CUSTOM is
        # "a real sheet, just not a standard size"; None is "this input never
        # stated a physical size at all", which is every raster.
        custom = ResponseDocumentProfile(page_count=1, paper_size=PaperSize.CUSTOM)
        raster = ResponseDocumentProfile(page_count=1, paper_size=None)

        assert custom.paper_size is PaperSize.CUSTOM
        assert raster.paper_size is None
        assert custom.paper_size != raster.paper_size

    def test_an_unrecognised_paper_size_is_rejected(self):
        # The point of using the enum rather than a bare str: a typo or a
        # server-side rename fails loudly here instead of flowing through.
        with pytest.raises(ValidationError):
            ResponseDocumentProfile(page_count=1, paper_size="A3 (ISO 216)")

    def test_it_round_trips_through_json(self):
        response = ResponseDocumentProfile(
            page_count=3,
            page_type=PageType.ASSEMBLY_DRAWING,
            paper_size=PaperSize.ANSI_D,
            processing_time=ProcessingTimeEstimate(seconds_p50=34.9, seconds_p95=120.0),
        )
        restored = ResponseDocumentProfile.model_validate_json(
            response.model_dump_json()
        )
        assert restored == response
        assert restored.processing_time.seconds_p95 == 120.0


class TestPaperSize:
    #: Every named format core-reader's `classify_paper_size` can return,
    #: verified against `_ISO_A_SERIES` + `_OTHER_FORMATS` in
    #: `lib/cost_tracking/document_shape.py` at the time of writing. Kept here
    #: as a literal because the client cannot import the reader: this is the
    #: contract between two repositories, and the only way it stays honest is
    #: by being written down on both sides and compared.
    READER_FORMATS = {
        "A6", "A5", "A4", "A3", "A2", "A1", "A0", "2A0",
        "ANSI_A", "ANSI_B", "ANSI_C", "ANSI_D", "ANSI_E",
        "ARCH_A", "ARCH_B", "ARCH_C", "ARCH_D", "ARCH_E", "ARCH_E1",
    }

    def test_it_covers_exactly_what_the_reader_emits(self):
        # Both directions matter. A format the reader can produce and this
        # enum cannot would fail validation on a real response; a member the
        # reader never produces is dead weight a caller would write a branch
        # for and never hit.
        named = {member.value for member in PaperSize} - {"CUSTOM"}

        assert named - self.READER_FORMATS == set(), "enum has formats the reader never emits"
        assert self.READER_FORMATS - named == set(), "reader emits formats the enum lacks"

    def test_custom_is_the_only_member_with_no_reader_format(self):
        # It stands for `custom_<A-series>`, which the reader emits for a real
        # sheet that matches no named format.
        assert "CUSTOM" not in self.READER_FORMATS
        assert PaperSize.CUSTOM.value == "CUSTOM"

    def test_values_are_tokens_like_every_other_v2_enum(self):
        # Not "A4 (ISO 216)". v1's W24PaperSize spells its values for humans;
        # mixing that style into a v2 response that also carries
        # COMPONENT_DRAWING and FIRST_ANGLE would be inconsistent.
        for member in PaperSize:
            assert member.value == member.value.strip()
            assert " " not in member.value
            assert "(" not in member.value

    def test_it_is_not_the_v1_enum(self):
        # Deliberately separate, and the reason is coverage as much as style:
        # v1 has no ARCH formats, no A6, and no way to say CUSTOM.
        from werk24.models.v1.paper_size import W24PaperSize

        v1_values = {member.value for member in W24PaperSize}
        assert "ARCH_C" not in v1_values
        assert "A6" not in v1_values
        assert "CUSTOM" not in v1_values


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
