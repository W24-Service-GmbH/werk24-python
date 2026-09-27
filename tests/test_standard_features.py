"""Tests for features a drawing specifies by a standard rather than by size.

A turned part names some of its features by standard: a thread undercut
(``DIN 76-B``), a relief groove at a shoulder (``DIN 509-E0,8x0,3``), a slot
for a parallel key (``DIN 6885 A 8x7x56``) or a center hole
(``DIN 332-A 2,5x5,3``). ``ResponseFeaturesComponentDrawing`` carries them in
``undercuts``, ``key_slots`` and ``center_holes``.

The lists default to empty so that a response from a server that predates
them still parses, and a client that predates them ignores them.
"""

from decimal import Decimal

from werk24 import (
    CenterHole,
    CenterHoleRequirement,
    KeySlot,
    ResponseFeaturesComponentDrawing,
    Size,
    SizeType,
    Undercut,
    UndercutType,
)


def _mm(value: str, size_type: SizeType = SizeType.LINEAR) -> Size:
    return Size(
        size_type=size_type, value=Decimal(value), tolerance=None, unit="millimeter"
    )


def _features(**kwargs) -> dict:
    return {"reference_id": 1, "confidence": None, **kwargs}


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
