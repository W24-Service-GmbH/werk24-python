"""Tests for angle dimensions on a component drawing.

An angle is dimensioned on an arc between two edges (``90°``), often with a
count (``4x 90°``) and sometimes with a tolerance (``30° ±0.5°``).
``ResponseFeaturesComponentDrawing`` carries them in ``angles``.

The list defaults to empty so that a response from a server that predates it
still parses, and a client that predates it ignores it.
"""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from werk24 import (
    Angle,
    Confidence,
    ResponseFeaturesComponentDrawing,
    Size,
    SizeType,
    Tolerance,
)


def _degrees(value: str, tolerance: Tolerance | None = None) -> Size:
    return Size(
        size_type=SizeType.ANGULAR,
        value=Decimal(value),
        tolerance=tolerance,
        unit="degree",
    )


def _right_angles() -> Angle:
    return Angle(
        reference_id=1,
        label="4x90°",
        confidence=Confidence(score=Decimal("0.97")),
        quantity=4,
        size=_degrees("90"),
    )


def _toleranced() -> Angle:
    return Angle(
        reference_id=2,
        label="30° ±0.5°",
        confidence=None,
        quantity=1,
        size=_degrees(
            "30",
            Tolerance(deviation_lower=Decimal("-0.5"), deviation_upper=Decimal("0.5")),
        ),
    )


def test_an_angle_carries_its_count_and_size():
    angle = _right_angles()
    assert angle.quantity == 4
    assert angle.size.size_type == SizeType.ANGULAR
    assert angle.size.value == Decimal("90")
    assert angle.size.unit == "degree"


def test_an_angle_carries_its_tolerance():
    tolerance = _toleranced().size.tolerance
    assert tolerance.deviation_lower == Decimal("-0.5")
    assert tolerance.deviation_upper == Decimal("0.5")


def test_the_quantity_is_at_least_one():
    with pytest.raises(ValidationError):
        Angle(
            reference_id=1,
            label="90°",
            confidence=None,
            quantity=0,
            size=_degrees("90"),
        )


def test_the_angle_round_trips_through_json():
    angle = _toleranced()
    assert Angle.model_validate_json(angle.model_dump_json()) == angle


def test_the_response_round_trips_the_angle_list():
    response = ResponseFeaturesComponentDrawing(
        angles=[_right_angles(), _toleranced()]
    )
    parsed = ResponseFeaturesComponentDrawing.model_validate_json(
        response.model_dump_json()
    )
    assert parsed.angles == response.angles


def test_a_response_without_the_angle_list_still_parses():
    parsed = ResponseFeaturesComponentDrawing.model_validate({})
    assert parsed.angles == []


def test_a_response_from_json_with_the_angle_list_parses():
    payload = {
        "angles": [
            {
                "reference_id": 7,
                "label": "3x120°",
                "confidence": None,
                "quantity": 3,
                "size": {
                    "size_type": "ANGULAR",
                    "value": "120",
                    "tolerance": None,
                    "unit": "degree",
                },
            }
        ]
    }
    parsed = ResponseFeaturesComponentDrawing.model_validate(payload)
    assert parsed.angles[0].quantity == 3
    assert parsed.angles[0].size.value == Decimal("120")
