"""Tests for the page assessment ask and response.

This ask exists because of what it costs. Every field in
``ResponseDocumentProfile`` is read straight off the file and arrives in
milliseconds; every field here waits on a vision call and arrives in seconds.
Keeping them in one response meant a caller who wanted the cheap answer paid
for the expensive one, which defeated the point of answering early at all.

So the split is the feature, and most of what is pinned here is the seam: that
the two asks stay separate, that this one carries per-page answers rather than
one answer for the document, and that "we could not look" stays distinct from
"we looked and found nothing".
"""

import pytest
from pydantic import ValidationError

from werk24.models.v2.asks import AskPageAssessment, get_ask_subclasses
from werk24.models.v2.enums import AskType, PageType
from werk24.models.v2.models import PageAssessment
from werk24.models.v2.responses import (
    RESPONSE_SUBCLASSES,
    ResponseDocumentProfile,
    ResponsePageAssessment,
)


class TestRegistration:
    def test_the_ask_registers_itself(self):
        # AskUnion is derived from __subclasses__, so an ask that is never
        # imported is an ask the server can never be sent.
        assert AskPageAssessment in get_ask_subclasses()

    def test_the_response_registers_itself(self):
        assert ResponsePageAssessment in RESPONSE_SUBCLASSES

    def test_the_ask_type_round_trips(self):
        ask = AskPageAssessment()
        assert ask.ask_type == AskType.PAGE_ASSESSMENT
        assert AskPageAssessment.model_validate_json(ask.model_dump_json()) == ask

    def test_it_is_a_different_ask_from_the_profile(self):
        # The whole point. If these ever collapse back into one ask, the fast
        # answer starts waiting on the slow one again.
        assert AskType.PAGE_ASSESSMENT != AskType.DOCUMENT_PROFILE
        assert set(ResponsePageAssessment.model_fields) != set(
            ResponseDocumentProfile.model_fields
        )


class TestPageAssessment:
    def test_the_two_answers_are_independent(self):
        # A page nobody could categorise may still plainly carry weld
        # callouts. Tying the welding answer to the page type would throw
        # away the better of two independent answers.
        assessment = PageAssessment(
            page_type=PageType.MISCELLANEOUS, has_welding_symbols=True
        )
        assert assessment.page_type is PageType.MISCELLANEOUS
        assert assessment.has_welding_symbols is True

    def test_it_defaults_to_claiming_nothing(self):
        # MISCELLANEOUS and False are both "we are not telling you anything",
        # which is the right default for a field a server may not populate.
        assessment = PageAssessment()
        assert assessment.page_type is PageType.MISCELLANEOUS
        assert assessment.has_welding_symbols is False

    def test_it_carries_a_plain_sentence(self):
        assessment = PageAssessment(
            page_type=PageType.MISCELLANEOUS,
            description="A cover sheet listing the drawings in this package.",
        )
        assert assessment.description.startswith("A cover sheet")

    def test_the_description_defaults_to_empty_not_none(self):
        # An empty string means "no sentence was produced". None would make
        # every caller reaching for `.description` handle a second case for
        # no gain, and there is no third state to express.
        assert PageAssessment().description == ""

    def test_the_description_is_what_rescues_miscellaneous(self):
        """MISCELLANEOUS on its own says only "not one of the categories".

        Two pages that are nothing alike get the same label, and the sentence
        is the only thing that tells them apart. This is the case the field
        was added for.
        """
        cover = PageAssessment(description="A cover sheet.")
        photo = PageAssessment(description="A photograph of a printed drawing.")

        assert cover.page_type is photo.page_type is PageType.MISCELLANEOUS
        assert cover.description != photo.description

    def test_an_unknown_page_type_degrades_rather_than_raising(self):
        # A category the server learns to recognise before this client knows
        # its name must not break a caller's pipeline on a real drawing.
        assessment = PageAssessment.model_validate({"page_type": "SOME_FUTURE_TYPE"})
        assert assessment.page_type is PageType.MISCELLANEOUS

    def test_a_known_page_type_stays_exact(self):
        assessment = PageAssessment.model_validate({"page_type": "PID_DRAWING"})
        assert assessment.page_type is PageType.PID_DRAWING


class TestResponse:
    def test_an_empty_response_is_valid(self):
        # A document we could not read at all still gets an answer, and an
        # empty list is the honest one.
        assert ResponsePageAssessment().pages == []

    def test_it_carries_one_entry_per_page_in_reading_order(self):
        response = ResponsePageAssessment(
            pages=[
                PageAssessment(page_type=PageType.COMPONENT_DRAWING),
                PageAssessment(page_type=PageType.ASSEMBLY_DRAWING),
            ]
        )
        assert [page.page_type for page in response.pages] == [
            PageType.COMPONENT_DRAWING,
            PageType.ASSEMBLY_DRAWING,
        ]

    def test_a_page_that_could_not_be_assessed_is_none_not_a_blank(self):
        # The distinction a training set depends on: None means nobody
        # looked, a default PageAssessment means somebody looked and saw an
        # ordinary page with no welds. Collapsing them would silently label
        # every failure as "no welding".
        response = ResponsePageAssessment(pages=[None, PageAssessment()])
        assert response.pages[0] is None
        assert response.pages[1] is not None
        assert response.pages[1].has_welding_symbols is False

    def test_a_none_entry_holds_its_position(self):
        # Dropping an unassessable page would shift every later page's index
        # and silently attribute one page's answer to another.
        response = ResponsePageAssessment(
            pages=[None, PageAssessment(page_type=PageType.PID_DRAWING), None]
        )
        assert len(response.pages) == 3
        assert response.pages[1].page_type is PageType.PID_DRAWING

    def test_it_round_trips_through_json(self):
        response = ResponsePageAssessment(
            pages=[
                PageAssessment(
                    page_type=PageType.ASSEMBLY_DRAWING, has_welding_symbols=True
                ),
                None,
            ]
        )
        restored = ResponsePageAssessment.model_validate_json(response.model_dump_json())
        assert restored == response
        assert restored.pages[0].has_welding_symbols is True
        assert restored.pages[1] is None

    def test_a_payload_from_a_newer_server_still_parses(self):
        response = ResponsePageAssessment.model_validate(
            {
                "pages": [
                    {"page_type": "SOME_FUTURE_TYPE", "has_welding_symbols": True},
                    None,
                ]
            }
        )
        assert response.pages[0].page_type is PageType.MISCELLANEOUS
        assert response.pages[0].has_welding_symbols is True

    def test_welding_must_be_a_boolean(self):
        # Presence is a yes or a no. A confidence dressed up as this field
        # would be read as a yes by every caller that does `if page.has_...`.
        with pytest.raises(ValidationError):
            PageAssessment(has_welding_symbols="probably")
