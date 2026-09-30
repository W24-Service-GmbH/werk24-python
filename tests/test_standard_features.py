"""Tests for features a drawing specifies by a standard rather than by size.

A turned part names some of its features by standard: a thread undercut
(``DIN 76-B``), a relief groove at a shoulder (``DIN 509-E0,8x0,3``), a slot
for a parallel key (``DIN 6885 A 8x7x56``) or a center hole
(``DIN 332-A 2,5x5,3``). ``ResponseFeaturesComponentDrawing`` carries them in
``undercuts``, ``key_slots`` and ``center_holes``.

Two features are sized on the drawing rather than by a standard alone: an
elongated hole with round ends (``2x Langloch 14x15``), carried in ``slots``,
and a groove for a retaining ring (``DIN 471 30x1,5``), carried in
``retaining_ring_grooves``. A center hole of one of the threaded forms of
DIN 332-2 (``DIN 332-D M16``) carries its thread.

The lists default to empty so that a response from a server that predates
them still parses, and a client that predates them ignores them.
"""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from werk24 import (
    CenterHole,
    CenterHoleRequirement,
    KeySlot,
    ResponseFeaturesComponentDrawing,
    RetainingRingGroove,
    RetainingRingSide,
    Size,
    SizeType,
    Slot,
    ThreadHandedness,
    ThreadISOMetric,
    ThreadSpacing,
    Undercut,
    UndercutType,
)


def _mm(value: str, size_type: SizeType = SizeType.LINEAR) -> Size:
    return Size(
        size_type=size_type, value=Decimal(value), tolerance=None, unit="millimeter"
    )


def _features(**kwargs) -> dict:
    return {"reference_id": 1, "confidence": None, **kwargs}


def _metric(diameter: str, pitch: str) -> ThreadISOMetric:
    return ThreadISOMetric(
        reference_id=1,
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


def _threaded_center_hole() -> CenterHole:
    return CenterHole(
        **_features(label="DIN 332-D M16"),
        quantity=1,
        standard="DIN 332",
        form="D",
        thread=_metric("16", "2"),
    )


def _slot() -> Slot:
    return Slot(
        **_features(label="2x Langloch 14x15"),
        quantity=2,
        width=_mm("14"),
        length=_mm("15"),
    )


def _retaining_ring_groove() -> RetainingRingGroove:
    return RetainingRingGroove(
        **_features(label="DIN 471 30x1,5"),
        quantity=1,
        standard="DIN 471",
        ring_side=RetainingRingSide.SHAFT,
        nominal_diameter=_mm("30", SizeType.DIAMETER),
        ring_thickness=_mm("1.5"),
    )


def test_a_relief_groove_carries_form_radius_and_depth():
    undercut = Undercut(
        **_features(label="DIN 509-E0,8x0,3"),
        quantity=1,
        undercut_type=UndercutType.RELIEF_GROOVE,
        standard="DIN 509",
        form="E",
        radius=_mm("0.8"),
        depth=_mm("0.3"),
    )

    assert undercut.form == "E"
    assert undercut.radius.value == Decimal("0.8")
    assert undercut.depth.value == Decimal("0.3")


def test_a_thread_undercut_needs_only_its_form():
    """DIN 76 sizes the groove from the thread pitch, so a drawing states the form."""
    undercut = Undercut(
        **_features(label="DIN 76-B"),
        quantity=1,
        undercut_type=UndercutType.THREAD_UNDERCUT,
        standard="DIN 76",
        form="B",
    )

    assert undercut.radius is None
    assert undercut.depth is None


def test_a_key_slot_carries_the_key_size():
    slot = KeySlot(
        **_features(label="DIN 6885 A 8x7x56"),
        quantity=1,
        standard="DIN 6885",
        form="A",
        key_width=_mm("8"),
        key_height=_mm("7"),
        key_length=_mm("56"),
    )

    assert (slot.key_width.value, slot.key_height.value, slot.key_length.value) == (
        Decimal("8"),
        Decimal("7"),
        Decimal("56"),
    )


def test_a_center_hole_carries_its_diameters_and_requirement():
    hole = CenterHole(
        **_features(label="2x DIN 332-A 2,5x5,3 (optional)"),
        quantity=2,
        standard="DIN 332",
        form="A",
        pilot_diameter=_mm("2.5", SizeType.DIAMETER),
        outer_diameter=_mm("5.3", SizeType.DIAMETER),
        requirement=CenterHoleRequirement.PERMITTED,
    )

    assert hole.quantity == 2
    assert hole.requirement is CenterHoleRequirement.PERMITTED


def test_the_response_round_trips_the_new_lists():
    response = ResponseFeaturesComponentDrawing(
        undercuts=[
            Undercut(
                **_features(label="DIN 76-B"),
                quantity=1,
                undercut_type=UndercutType.THREAD_UNDERCUT,
                standard="DIN 76",
                form="B",
            )
        ],
        key_slots=[
            KeySlot(
                **_features(label="DIN 6885 A 8x7x56"),
                quantity=1,
                standard="DIN 6885",
                key_width=_mm("8"),
            )
        ],
        center_holes=[
            CenterHole(**_features(label="DIN 332"), quantity=1, standard="DIN 332")
        ],
    )

    restored = ResponseFeaturesComponentDrawing.model_validate_json(
        response.model_dump_json()
    )

    assert restored == response


def test_a_response_without_the_new_lists_still_parses():
    """A server that predates the fields sends none of them."""
    restored = ResponseFeaturesComponentDrawing.model_validate({"bores": []})

    assert restored.undercuts == []
    assert restored.key_slots == []
    assert restored.center_holes == []


def test_a_threaded_center_hole_carries_its_thread():
    hole = _threaded_center_hole()

    restored = CenterHole.model_validate_json(hole.model_dump_json())

    assert restored == hole
    assert isinstance(restored.thread, ThreadISOMetric)
    assert restored.thread.diameter.value == Decimal("16")


def test_a_threaded_center_hole_may_state_the_countersink_instead():
    """``DIN 332-D 8,4x12,2`` is the M8 row, written by its countersink.

    DIN 332-2 table 1, M8: d3 = 8.4 and d4 = 12.2. d4 is the outer diameter;
    d3 is fixed by the thread, which carries it.
    """
    hole = CenterHole(
        **_features(label="DIN 332-D 8,4x12,2"),
        quantity=1,
        standard="DIN 332",
        form="D",
        outer_diameter=_mm("12.2", SizeType.DIAMETER),
        thread=_metric("8", "1.25"),
    )
    restored = CenterHole.model_validate_json(hole.model_dump_json())

    assert restored == hole
    assert restored.thread.diameter.value == Decimal("8")
    assert restored.outer_diameter.value == Decimal("12.2")
    assert restored.pilot_diameter is None


def test_a_center_hole_without_a_thread_has_none():
    hole = CenterHole(
        **_features(label="DIN 332-A 2,5x5,3"),
        quantity=1,
        standard="DIN 332",
        form="A",
    )

    assert hole.thread is None
    assert CenterHole.model_validate_json(hole.model_dump_json()).thread is None


def test_a_center_hole_payload_without_a_thread_still_parses():
    """A server that predates the field does not send it."""
    hole = CenterHole.model_validate(
        {
            "reference_id": 1,
            "label": "DIN 332-A 2,5x5,3",
            "confidence": None,
            "quantity": 1,
            "standard": "DIN 332",
            "form": "A",
        }
    )

    assert hole.thread is None


def test_a_slot_carries_width_and_length():
    slot = _slot()

    restored = Slot.model_validate_json(slot.model_dump_json())

    assert restored == slot
    assert (restored.width.value, restored.length.value) == (
        Decimal("14"),
        Decimal("15"),
    )


def test_a_slot_written_with_a_diameter_needs_only_its_width():
    """``Ø 10`` is the width of the slot, reported as a linear size."""
    slot = Slot(
        **_features(label="3x Langloch Ø 10"),
        quantity=3,
        width=_mm("10"),
    )

    assert slot.width.size_type is SizeType.LINEAR
    assert slot.label == "3x Langloch Ø 10"
    assert slot.length is None


def test_a_slot_needs_at_least_one_instance():
    with pytest.raises(ValidationError):
        Slot(**_features(label="Langloch Ø 10"), quantity=0, width=_mm("10"))


def test_a_retaining_ring_groove_carries_the_ring_size():
    groove = _retaining_ring_groove()

    restored = RetainingRingGroove.model_validate_json(groove.model_dump_json())

    assert restored == groove
    assert restored.ring_side is RetainingRingSide.SHAFT
    assert restored.nominal_diameter.value == Decimal("30")
    assert restored.ring_thickness.value == Decimal("1.5")


def test_a_retaining_ring_groove_may_name_only_a_designation():
    """A maker's designation is reported as written, not decoded."""
    groove = RetainingRingGroove(
        **_features(label="Seeger RB 042"),
        quantity=1,
        designation="RB 042",
        manufacturer="Seeger",
    )

    assert groove.standard is None
    assert groove.ring_side is None
    assert groove.nominal_diameter is None
    assert groove.designation == "RB 042"


def test_the_retaining_ring_side_serializes_as_its_name():
    assert RetainingRingSide("BORE") is RetainingRingSide.BORE
    assert RetainingRingSide.SHAFT.value == "SHAFT"


def test_the_response_round_trips_slots_and_retaining_ring_grooves():
    response = ResponseFeaturesComponentDrawing(
        center_holes=[_threaded_center_hole()],
        slots=[_slot()],
        retaining_ring_grooves=[_retaining_ring_groove()],
    )

    restored = ResponseFeaturesComponentDrawing.model_validate_json(
        response.model_dump_json()
    )

    assert restored == response
    assert isinstance(restored.center_holes[0].thread, ThreadISOMetric)


def test_a_response_without_slots_or_retaining_ring_grooves_still_parses():
    """A server that predates the fields sends neither."""
    restored = ResponseFeaturesComponentDrawing.model_validate(
        {"center_holes": [], "key_slots": []}
    )

    assert restored.slots == []
    assert restored.retaining_ring_grooves == []
