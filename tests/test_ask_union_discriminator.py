"""``AskUnion`` resolves by tag, not by trying its members in order.

``AskUnion`` is a 37-member union and every member already carries its own
``ask_type`` as a ``Literal``. Without ``Field(discriminator="ask_type")``
pydantic still validated an ask against member after member until one accepted
it, which costs on the order of 470us per three-ask payload -- paid on every
DynamoDB read and write of a request row in crew-api (crew-api#144), and on
every ask list the client sends.

With the discriminator the tag selects the one member that can match, at about
2.7us for the same payload.

The companion file ``test_ask_union_resolution.py`` covers *which* class comes
back. This one covers that the tag is what chooses it, and the two properties
the discriminator relies on: exactly one member per ask_type, and no member
without one.
"""

import pytest
from pydantic import TypeAdapter, ValidationError

from werk24 import AskUnion
from werk24.models.v2.asks import get_ask_subclasses

ADAPTER = TypeAdapter(list[AskUnion])


def test_every_member_names_exactly_one_ask_type():
    """The precondition for discriminating on it at all.

    A tag claimed by two members makes the union ambiguous, and pydantic
    refuses to build the schema rather than pick one.
    """
    tags = [
        subclass.model_fields["ask_type"].default
        for subclass in get_ask_subclasses()
    ]
    assert len(tags) == len(set(tags))
    assert all(tag is not None for tag in tags)


def test_the_tag_selects_the_class():
    asks = ADAPTER.validate_python(
        [{"ask_type": "NOTES"}, {"ask_type": "FEATURES"}]
    )
    assert [type(ask).__name__ for ask in asks] == ["W24AskNotes", "AskFeatures"]


def test_an_unknown_tag_is_refused_rather_than_guessed():
    """The behaviour change worth knowing about.

    Trying members in order meant an ask with an unrecognised ``ask_type``
    could still be accepted by whichever permissive member happened to come
    first. A tagged union says so instead.
    """
    with pytest.raises(ValidationError):
        ADAPTER.validate_python([{"ask_type": "NOT_AN_ASK"}])


def test_a_missing_tag_is_refused():
    with pytest.raises(ValidationError):
        ADAPTER.validate_python([{}])


def _tag_only_members():
    """Members that can be built from their tag alone.

    Three asks (CUSTOM, PART_FAMILY_CHARACTERIZATION, SHEET_REBRANDING) carry
    required fields of their own, so a bare tag is not a valid payload for
    them and they are covered by the mapping test below instead.
    """
    for subclass in get_ask_subclasses():
        others = [
            name
            for name, field in subclass.model_fields.items()
            if name != "ask_type" and field.is_required()
        ]
        if not others:
            yield subclass


@pytest.mark.parametrize(
    "subclass", list(_tag_only_members()), ids=lambda cls: cls.__name__
)
def test_every_ask_type_round_trips_as_itself(subclass):
    tag = subclass.model_fields["ask_type"].default
    value = tag.value if hasattr(tag, "value") else tag
    (ask,) = ADAPTER.validate_python([{"ask_type": value}])
    assert type(ask) is subclass
    assert ask.ask_type == tag


def test_the_tagged_union_covers_every_member():
    """No ask is unreachable.

    A discriminator is all-or-nothing: a member the mapping does not name
    cannot be produced at all, which would be a silent regression rather than
    a loud one. This walks the built schema rather than the type alias, so it
    fails if pydantic dropped a member while building.
    """
    found = []

    def walk(node):
        if isinstance(node, dict):
            if node.get("type") == "tagged-union":
                found.append(node)
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)

    walk(ADAPTER.core_schema)
    assert found, "AskUnion did not build as a tagged union"
    assert len(found[0]["choices"]) == len(get_ask_subclasses())
