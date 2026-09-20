"""Tests for the origin of a material specification.

Two drawings can list the same two materials and mean different things.
"1.4301 OR 1.4404" written in a single canvas note is a choice the designer
offers; "1.4301" in the title block with "alternative material 1.4404" in a
canvas note is a primary material with a fallback. Both arrive as two entries
in ``material_options``, so without ``Material.origin`` a consumer cannot tell
the two cases apart.

The field is optional and defaults to None so that producers and consumers
predating it keep working unchanged.
"""

import pytest

from werk24 import Material, MaterialCombination
from werk24.models import MaterialOrigin
from werk24.models.v1.material import W24Material, W24MaterialOrigin


def _material(designation: str, origin: MaterialOrigin | None = None) -> Material:
    return Material(
        raw_ocr=designation,
        standard="EN 10088-3",
        designation=designation,
        material_category=(None, None, None),
        origin=origin,
    )


def test_origin_defaults_to_none():
    """A reading that carries no attribution stays unattributed."""
    material = Material(
        raw_ocr="1.4301",
        standard=None,
        designation="X5CrNi18-10",
        material_category=(None, None, None),
    )

    assert material.origin is None


@pytest.mark.parametrize("origin", list(MaterialOrigin))
def test_every_origin_survives_a_round_trip(origin: MaterialOrigin):
    payload = _material("1.4301", origin).model_dump(mode="json")

    assert payload["origin"] == origin.value
    assert Material.model_validate(payload).origin is origin


def test_two_canvas_note_materials_differ_from_a_mixed_pair():
    """The distinction the field exists for.

    Both option lists hold the same two designations; only the origins say
    whether the alternative was offered in the same note or added by one.
    """
    both_in_a_note = [
        MaterialCombination(
            reference_id=1,
            material_combination=[_material("1.4301", MaterialOrigin.CANVAS_NOTE)],
        ),
        MaterialCombination(
            reference_id=1,
            material_combination=[_material("1.4404", MaterialOrigin.CANVAS_NOTE)],
        ),
    ]
    title_block_plus_note = [
        MaterialCombination(
            reference_id=1,
            material_combination=[_material("1.4301", MaterialOrigin.TITLE_BLOCK)],
        ),
        MaterialCombination(
            reference_id=2,
            material_combination=[_material("1.4404", MaterialOrigin.CANVAS_NOTE)],
        ),
    ]

    def origins(options: list[MaterialCombination]) -> list[MaterialOrigin | None]:
        return [m.origin for option in options for m in option.material_combination]

    assert origins(both_in_a_note) == [
        MaterialOrigin.CANVAS_NOTE,
        MaterialOrigin.CANVAS_NOTE,
    ]
    assert origins(title_block_plus_note) == [
        MaterialOrigin.TITLE_BLOCK,
        MaterialOrigin.CANVAS_NOTE,
    ]
    assert origins(both_in_a_note) != origins(title_block_plus_note)


def test_materials_of_one_combination_may_disagree():
    """A base metal in the title block, its coating called out in a note."""
    combination = MaterialCombination(
        reference_id=7,
        material_combination=[
            _material("1.4301", MaterialOrigin.TITLE_BLOCK),
            _material("ZN 8", MaterialOrigin.CANVAS_NOTE),
        ],
    )

    assert [m.origin for m in combination.material_combination] == [
        MaterialOrigin.TITLE_BLOCK,
        MaterialOrigin.CANVAS_NOTE,
    ]


def test_v1_and_v2_origins_share_their_values():
    """core-reader reads into the v1 model and exports the v2 one.

    The v1 enum is a separate definition because v1 must not import from v2,
    so nothing but a test stops the two from drifting apart.
    """
    assert {o.name for o in W24MaterialOrigin} == {o.name for o in MaterialOrigin}
    assert {o.value for o in W24MaterialOrigin} == {o.value for o in MaterialOrigin}


def test_v1_origin_defaults_to_none():
    material = W24Material(
        blurb="X5CrNi18-10",
        raw_ocr_blurb="1.4301",
        standard="EN 10088-3",
        designation="X5CrNi18-10",
        material_category=(None, None, None),
    )

    assert material.origin is None
