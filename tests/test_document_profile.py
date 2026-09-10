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

    def test_a_p95_below_the_median_is_rejected(self):
        # This object exists to be acted on: a caller sizing a timeout against
        # seconds_p95 would silently get one shorter than the median it is
        # meant to bound, and nothing downstream would notice.
        with pytest.raises(ValidationError):
            ProcessingTimeEstimate(seconds_p50=40.0, seconds_p95=10.0)

    def test_equal_percentiles_are_allowed(self):
        # A sheet size with few observations can genuinely report the same
        # value at both. Rejecting that would turn a thin distribution into an
        # error.
        estimate = ProcessingTimeEstimate(seconds_p50=5.0, seconds_p95=5.0)
        assert estimate.seconds_p50 == estimate.seconds_p95

    def test_non_positive_durations_are_rejected(self):
        for p50, p95 in [(-1.0, 10.0), (0.0, 10.0), (5.0, 0.0)]:
            with pytest.raises(ValidationError):
                ProcessingTimeEstimate(seconds_p50=p50, seconds_p95=p95)


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

    def test_an_unrecognised_paper_size_degrades_to_custom(self):
        """Replaces an earlier test that asserted the opposite.

        That test argued a typo should fail loudly. In production the "typo"
        is a server-side addition, and failing loudly means breaking a
        caller's pipeline on a real drawing. CUSTOM already means "a real
        sheet that is not one of the formats we name", which is exactly what
        an unknown format is from an older client's position, so degrading is
        a definition rather than a fudge.
        """
        response = ResponseDocumentProfile(page_count=1, paper_size="ARCH_F")
        assert response.paper_size is PaperSize.CUSTOM

    def test_page_count_must_be_at_least_one(self):
        # A document with zero pages is not a document.
        for count in (0, -1):
            with pytest.raises(ValidationError):
                ResponseDocumentProfile(page_count=count)

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


class TestForwardCompatibility:
    """A client older than the server must degrade, not raise.

    Both of these enums carry values the SERVER chooses and the client only
    reads. Without a fallback, the first time either gained a member, every
    client released before that day would fail validation on a perfectly good
    drawing — the worst possible failure mode for a library whose whole job is
    to hand back what the server found.
    """

    def test_an_unknown_page_type_becomes_miscellaneous(self):
        assert PageType("SOME_FUTURE_TYPE") is PageType.MISCELLANEOUS

    def test_an_unknown_paper_size_becomes_custom(self):
        assert PaperSize("ARCH_F") is PaperSize.CUSTOM

    def test_a_response_carrying_unknown_values_still_parses(self):
        # The case that matters: a whole payload from a newer server.
        response = ResponseDocumentProfile.model_validate(
            {
                "page_count": 2,
                "page_type": "SOME_FUTURE_TYPE",
                "paper_size": "ARCH_F",
                "processing_time": {"seconds_p50": 20.0, "seconds_p95": 45.0},
            }
        )
        assert response.page_type is PageType.MISCELLANEOUS
        assert response.paper_size is PaperSize.CUSTOM
        assert response.processing_time.seconds_p50 == 20.0

    def test_known_values_are_still_exact(self):
        # The fallback must not swallow values we do know.
        assert PageType("PID_DRAWING") is PageType.PID_DRAWING
        assert PaperSize("ANSI_D") is PaperSize.ANSI_D


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
