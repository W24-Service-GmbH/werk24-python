"""Tests for fasteners on the drawing and in the bill of material.

A sheet-metal part names the fasteners that are pressed into it or welded
onto it: a press-in nut (``3x PEM CLS-M4-2``), a weld nut (``4x DIN 929 M12``)
or a weld stud (``6x M6x15``); an assembly lists screws, nuts and washers
(``ISO 4762 M6x20``). ``ResponseFeaturesComponentDrawing`` carries the
callouts in ``fasteners``, and a bill of material row that lists a fastener
carries the same description in ``BillOfMaterialRow.fastener``.

Both default to empty so that a response from a server that predates them
still parses, and a client that predates them ignores them.
"""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from werk24 import (
    BillOfMaterial,
    BillOfMaterialRow,
    Fastener,
    FastenerSpecification,
    FastenerType,
    ResponseFeaturesComponentDrawing,
    Size,
    SizeType,
    ThreadHandedness,
    ThreadISOMetric,
    ThreadSpacing,
)


def _mm(value: str, size_type: SizeType = SizeType.LINEAR) -> Size:
    return Size(
        size_type=size_type, value=Decimal(value), tolerance=None, unit="millimeter"
    )


def _metric(diameter: str, pitch: str, reference_id: int = 1) -> ThreadISOMetric:
    return ThreadISOMetric(
        reference_id=reference_id,
        label=f"M{diameter}",
        confidence=None,
        quantity=Decimal("1"),
        diameter=_mm(diameter, SizeType.DIAMETER),
        spacing=ThreadSpacing(
            pitch_in_mm=Decimal(pitch),
            threads_per_inch=(Decimal("25.4") / Decimal(pitch)).quantize(
                Decimal("0.001")
            ),
        ),
        handedness=ThreadHandedness.RIGHT,
    )


def _press_in_nut() -> Fastener:
    return Fastener(
        reference_id=1,
        label="3x PEM CLS-M4-2",
        confidence=None,
        quantity=3,
        fastener_type=FastenerType.PRESS_IN_NUT,
        designation="PEM CLS-M4-2",
        manufacturer="PEM",
        thread=_metric("4", "0.7"),
    )


def _weld_stud() -> Fastener:
    return Fastener(
        reference_id=2,
        label="6x weld stud M6x15 pointing inward",
        confidence=None,
        quantity=6,
        fastener_type=FastenerType.WELD_STUD,
        thread=_metric("6", "1", reference_id=2),
        length=_mm("15"),
        note="pointing inward",
    )


def test_the_enum_names_how_the_fastener_is_joined():
    assert [t.value for t in FastenerType] == [
        "PRESS_IN_NUT",
        "PRESS_IN_STUD",
        "PRESS_IN_STANDOFF",
        "WELD_NUT",
        "WELD_STUD",
        "THREADED_INSERT",
        "RIVET_NUT",
        "SCREW",
        "NUT",
        "WASHER",
        "OTHER",
    ]
    assert FastenerType("WELD_NUT") is FastenerType.WELD_NUT


def test_a_press_in_nut_carries_its_designation_and_thread():
    nut = _press_in_nut()

    assert nut.fastener_type is FastenerType.PRESS_IN_NUT
    assert nut.designation == "PEM CLS-M4-2"
    assert nut.manufacturer == "PEM"
    assert nut.thread.diameter.value == Decimal("4")
    assert nut.thread.spacing.pitch_in_mm == Decimal("0.7")
    # The shank code 2 is not a length.
    assert nut.length is None
    assert nut.standard is None
    assert nut.note is None


def test_a_weld_nut_carries_its_standard():
    nut = Fastener(
        reference_id=3,
        label="4x DIN 929 M12",
        confidence=None,
        quantity=4,
        fastener_type=FastenerType.WELD_NUT,
        designation="DIN 929 M12",
        standard="DIN 929",
        thread=_metric("12", "1.75", reference_id=3),
    )

    assert nut.standard == "DIN 929"
    assert nut.thread.diameter.value == Decimal("12")


def test_a_weld_stud_carries_its_length_and_placement():
    stud = _weld_stud()

    assert stud.designation is None
    assert stud.length.value == Decimal("15")
    assert stud.note == "pointing inward"


def test_a_washer_has_no_thread():
    washer = FastenerSpecification(
        fastener_type=FastenerType.WASHER,
        designation="ISO 7089 8",
        standard="ISO 7089",
    )

    assert washer.thread is None
    assert washer.length is None


def test_the_quantity_is_at_least_one():
    with pytest.raises(ValidationError):
        Fastener(
            reference_id=1,
            label="M5",
            confidence=None,
            quantity=0,
            fastener_type=FastenerType.PRESS_IN_NUT,
        )


def test_a_fastener_is_a_fastener_specification():
    """So a callout and a BOM row can be compared on the same fields."""
    assert isinstance(_press_in_nut(), FastenerSpecification)


def test_the_fastener_round_trips_through_json():
    for fastener in (_press_in_nut(), _weld_stud()):
        restored = Fastener.model_validate_json(fastener.model_dump_json())
        assert restored == fastener
        assert isinstance(restored.thread, ThreadISOMetric)


def test_the_response_round_trips_the_fastener_list():
    response = ResponseFeaturesComponentDrawing(
        fasteners=[_press_in_nut(), _weld_stud()]
    )

    restored = ResponseFeaturesComponentDrawing.model_validate_json(
        response.model_dump_json()
    )

    assert restored == response
    assert [f.fastener_type for f in restored.fasteners] == [
        FastenerType.PRESS_IN_NUT,
        FastenerType.WELD_STUD,
    ]


def test_a_response_without_the_fastener_list_still_parses():
    """A server that predates the field sends none of it."""
    restored = ResponseFeaturesComponentDrawing.model_validate({"bores": []})

    assert restored.fasteners == []


def test_a_response_from_json_with_the_fastener_list_parses():
    payload = {
        "fasteners": [
            {
                "reference_id": 7,
                "label": "4x DIN 929 M12",
                "confidence": {"score": "0.95"},
                "fastener_type": "WELD_NUT",
                "designation": "DIN 929 M12",
                "standard": "DIN 929",
                "manufacturer": None,
                "thread": {
                    "thread_type": "ISO_METRIC",
                    "reference_id": 7,
                    "label": "M12",
                    "confidence": None,
                    "quantity": "1",
                    "diameter": {
                        "size_type": "DIAMETER",
                        "value": "12",
                        "unit": "millimeter",
                    },
                    "spacing": {"pitch_in_mm": "1.75", "threads_per_inch": "14.514"},
                    "handedness": "RIGHT",
                },
                "length": None,
                "quantity": 4,
                "note": None,
            }
        ]
    }

    restored = ResponseFeaturesComponentDrawing.model_validate(payload)

    (nut,) = restored.fasteners
    assert nut.fastener_type is FastenerType.WELD_NUT
    assert isinstance(nut.thread, ThreadISOMetric)
    assert nut.thread.spacing.pitch_in_mm == Decimal("1.75")


def test_a_bom_row_without_a_fastener_still_parses():
    """A server that predates the field sends rows without it."""
    row = BillOfMaterialRow.model_validate(
        {"position": "1", "designation": "Housing", "material_options": []}
    )

    assert row.fastener is None


def test_a_bom_row_with_a_fastener_round_trips():
    row = BillOfMaterialRow(
        position="3",
        part_number="CLS-M4-2",
        designation="Press-in nut PEM CLS-M4-2",
        fastener=FastenerSpecification(
            fastener_type=FastenerType.PRESS_IN_NUT,
            designation="PEM CLS-M4-2",
            manufacturer="PEM",
            thread=_metric("4", "0.7"),
        ),
    )
    screw = BillOfMaterialRow(
        position="4",
        designation="ISO 4762 M6x20",
        fastener=FastenerSpecification(
            fastener_type=FastenerType.SCREW,
            designation="ISO 4762 M6x20",
            standard="ISO 4762",
            thread=_metric("6", "1"),
            length=_mm("20"),
        ),
    )
    table = BillOfMaterial(reference_id=1, rows=[row, screw])

    restored = BillOfMaterial.model_validate_json(table.model_dump_json())

    assert restored == table
    assert [r.fastener.fastener_type for r in restored.rows] == [
        FastenerType.PRESS_IN_NUT,
        FastenerType.SCREW,
    ]


def test_a_bom_row_and_a_callout_describe_the_same_fastener_alike():
    callout = _press_in_nut()
    row = BillOfMaterialRow(
        fastener=FastenerSpecification(
            **{
                name: getattr(callout, name)
                for name in FastenerSpecification.model_fields
            }
        )
    )

    for name in FastenerSpecification.model_fields:
        assert getattr(row.fastener, name) == getattr(callout, name)
