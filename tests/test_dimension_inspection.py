"""Tests for a dimension marked for inspection.

A drawing marks a dimension for inspection by drawing an inspection frame
(the stadium-shaped frame with rounded ends) around it, sometimes with a
criticality and an inspection rate in fields of its own
(``CTF | 25 ±0.1 | 100%``). ``Dimension.inspection`` carries that mark, as
``GDnT.inspection`` does for a feature control frame.

It defaults to None, so a response from a server that predates it still
parses and a dimension without the mark looks as before.
"""

from decimal import Decimal

from werk24 import (
    Dimension,
    Inspection,
    InspectionCriticality,
    ResponseFeaturesComponentDrawing,
    Size,
    SizeType,
    Tolerance,
)


def _dimension(**kwargs) -> Dimension:
    return Dimension(
        reference_id=7,
        label="25 ±0.1",
        confidence=None,
        quantity=1,
        size=Size(
            size_type=SizeType.LINEAR,
            value=Decimal("25"),
            unit="millimeter",
            tolerance=Tolerance(
                deviation_lower=Decimal("-0.1"), deviation_upper=Decimal("0.1")
            ),
        ),
        **kwargs,
    )


def test_without_the_mark_it_is_none():
    assert _dimension().inspection is None


def test_criticality_and_rate():
    dimension = _dimension(
        inspection=Inspection(
            criticality=InspectionCriticality.CRITICAL_TO_FUNCTION,
            rate=Decimal("100"),
        )
    )
    assert (
        dimension.inspection.criticality is InspectionCriticality.CRITICAL_TO_FUNCTION
    )
    assert dimension.inspection.rate == Decimal("100")


def test_round_trips_through_json():
    dimension = _dimension(inspection=Inspection(criticality="CTQ"))
    again = Dimension.model_validate_json(dimension.model_dump_json())
    assert again == dimension
    assert dimension.model_dump(mode="json")["inspection"] == {
        "criticality": "CTQ",
        "rate": None,
    }


def test_an_older_payload_without_the_field_parses():
    payload = _dimension().model_dump(mode="json")
    del payload["inspection"]
    assert Dimension.model_validate(payload).inspection is None


def test_the_mark_reaches_the_features_response():
    marked = _dimension(inspection=Inspection())
    response = ResponseFeaturesComponentDrawing.model_validate(
        {"dimensions": [marked.model_dump(mode="json")]}
    )
    assert response.dimensions[0].inspection == Inspection()
