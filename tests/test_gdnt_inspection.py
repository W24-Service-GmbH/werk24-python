"""Tests for a GD&T frame marked for inspection.

A drawing can draw a feature control frame inside an inspection frame (the
stadium-shaped frame with rounded ends), e.g. a circularity of 0.12 that is
to be inspected on every part. ``GDnT.inspection`` (v2) and
``W24GDTFrame.test_dimension`` (v1) carry that mark.

Both default to None, so a response from a server that predates them still
parses and a frame without the mark looks as before.
"""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from werk24 import (
    GDnT,
    GDnTCharacteristic,
    GDnTZone,
    Inspection,
    InspectionCriticality,
    Size,
    SizeType,
)
from werk24.models.v1.gdt import (
    W24GDTCharacteristic,
    W24GDTFrame,
    W24GDTZoneValue,
)
from werk24.models.v1.test_dimension import W24TestCriticality, W24TestDimension


def _circularity(**kwargs) -> GDnT:
    return GDnT(
        reference_id=14,
        label="[○|0.12]",
        confidence=None,
        characteristic=GDnTCharacteristic.CIRCULARITY,
        zone=GDnTZone(
            value=Size(
                size_type=SizeType.LINEAR,
                value=Decimal("0.12"),
                tolerance=None,
                unit="millimeter",
            )
        ),
        feature=None,
        reference=None,
        **kwargs,
    )


class TestV2:
    def test_without_the_mark_it_is_none(self):
        assert _circularity().inspection is None

    def test_a_marked_frame(self):
        gdnt = _circularity(inspection=Inspection())
        assert gdnt.inspection == Inspection(criticality=None, rate=None)

    def test_criticality_and_rate(self):
        gdnt = _circularity(
            inspection=Inspection(
                criticality=InspectionCriticality.CRITICAL_TO_FUNCTION,
                rate=Decimal("100"),
            )
        )
        assert gdnt.inspection.criticality is InspectionCriticality.CRITICAL_TO_FUNCTION
        assert gdnt.inspection.rate == Decimal("100")

    def test_round_trips_through_json(self):
        gdnt = _circularity(
            inspection=Inspection(criticality="CTQ", rate=Decimal("10"))
        )
        again = GDnT.model_validate_json(gdnt.model_dump_json())
        assert again == gdnt
        assert gdnt.model_dump(mode="json")["inspection"] == {
            "criticality": "CTQ",
            "rate": "10",
        }

    def test_an_older_payload_without_the_field_parses(self):
        payload = _circularity().model_dump(mode="json")
        del payload["inspection"]
        assert GDnT.model_validate(payload).inspection is None

    @pytest.mark.parametrize("rate", ["-1", "100.5"])
    def test_a_rate_outside_0_to_100_is_refused(self, rate):
        with pytest.raises(ValidationError):
            Inspection(rate=Decimal(rate))

    def test_the_criticalities_match_v1(self):
        assert {c.value for c in InspectionCriticality} == {
            c.value for c in W24TestCriticality
        }


class TestV1:
    def _frame(self, **kwargs) -> W24GDTFrame:
        return W24GDTFrame(
            blurb="[○|0.12]",
            characteristic=W24GDTCharacteristic.FORM_CIRCULARITY,
            zone_value=W24GDTZoneValue(
                blurb="0.12",
                width_min=Decimal("0.12"),
                width_max=None,
                extend_quantity=None,
                extend_shape=None,
                extend_value=None,
                extend_angle=None,
            ),
            **kwargs,
        )

    def test_without_the_mark_it_is_none(self):
        assert self._frame().test_dimension is None

    def test_a_marked_frame(self):
        frame = self._frame(
            test_dimension=W24TestDimension(
                blurb="(○|0.12)",
                criticality=W24TestCriticality.CRITICAL_TO_FUNCTION,
                rate=Decimal("100"),
            )
        )
        again = W24GDTFrame.model_validate_json(frame.model_dump_json())
        assert again.test_dimension == frame.test_dimension
        assert again.test_dimension.rate == Decimal("100")
