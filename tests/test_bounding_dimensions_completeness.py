"""Tests for the annotation-completeness fields on BoundingDimensions.

Some drawings never dimension the component's outermost geometry: tabs,
winglets, lugs, standoffs and welded-on brackets are drawn but no dimension
line reaches them. The extracted bounding dimensions are then a lower bound
rather than an exact figure, and consumers need to be told so.

Both fields default so that existing producers and consumers of
BoundingDimensions keep working unchanged.
"""

from decimal import Decimal

from werk24 import BoundingDimensions, GeometryCuboid, Size, SizeType


def _size(value: str) -> Size:
    return Size(size_type=SizeType.LINEAR, value=Decimal(value), unit="mm")


def _cuboid() -> GeometryCuboid:
    return GeometryCuboid(
        width=_size("47.14"),
        height=_size("44.54"),
        depth=_size("4.60"),
    )


def test_defaults_to_complete():
    """An unqualified reading is assumed to cover the whole envelope."""
    dims = BoundingDimensions(enclosing_cuboid=_cuboid())

    assert dims.annotations_complete is True
    assert dims.completeness_note is None


def test_incomplete_annotations_carry_a_reason():
    note = (
        "The winglets on the side panels carry no dimensions, so the depth "
        "is a lower bound and the true envelope is slightly larger."
    )
    dims = BoundingDimensions(
        enclosing_cuboid=_cuboid(),
        annotations_complete=False,
        completeness_note=note,
    )

    assert dims.annotations_complete is False
    assert dims.completeness_note == note
    # The dimensions themselves are still reported — a close lower bound is
    # more useful than no answer.
    assert dims.enclosing_cuboid.depth.value == Decimal("4.60")


def test_fields_round_trip_through_json():
    dims = BoundingDimensions(
        enclosing_cuboid=_cuboid(),
        annotations_complete=False,
        completeness_note="lift lug is undimensioned",
    )

    restored = BoundingDimensions.model_validate(dims.model_dump(mode="json"))

    assert restored.annotations_complete is False
    assert restored.completeness_note == "lift lug is undimensioned"


def test_backwards_compatible_with_payloads_lacking_the_fields():
    """Older servers omit both fields; the reading is then taken as complete."""
    restored = BoundingDimensions.model_validate(
        {"enclosing_cuboid": None, "enclosing_cylinder": None}
    )

    assert restored.annotations_complete is True
    assert restored.completeness_note is None
