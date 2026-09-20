"""`W24IdentifierType` is the vocabulary a read can use for a title block ID.

The reader's caption assets define one dimension per identifier kind
(`IDENTIFIER/<NAME>`) and already recognise captions for far more kinds than
this enum could express. Where a dimension had no member here the read fell
back to `NUMBER`, which keeps the caption and the value but loses the kind, so
the gap was invisible in the output and showed up only as a generic number.

These tests pin the members that closed that gap, and pin the two spellings
that are wrong on purpose: correcting either changes a value customers already
receive, so both want a deprecation cycle rather than an edit in passing.
"""

import json
import re

import pytest

from werk24.models.v1.title_block import (
    W24IdentifierPeriod,
    W24IdentifierStakeholder,
    W24IdentifierType,
)
from werk24.models.v2.enums import IdentifierType

#: v1 spells two members wrong and v2 already corrected both, so the two enums
#: cannot be compared member-for-member without saying so here.
_V1_ONLY = {"ITEM_NUMER"}
_V2_ONLY = {"ITEM_NUMBER"}

#: Added because the reader's caption assets already carry these dimensions.
ADDED = (
    "CUSTOMER_INDEX",
    "DASH_NUMBER",
    "DOCUMENT_CODE",
    "ERP_CHANGE_NUMBER",
    "FINANCIAL_SUPPLY_CHAIN_MANAGEMENT_NUMBER",
    "GROUP_NUMBER",
    "JOB_NUMBER",
    "MODEL",
    "PRODUCT_NAME",
    "PRODUCT_NUMBER",
    "PROFILE_NUMBER",
    "PROJECT_NUMBER",
    "PROTOTYPE_NUMBER",
    "SERIAL_NUMBER",
    "SETTING_PLAN_NUMBER",
    "TOOL_NUMBER",
    "TYPE_NUMBER",
)


@pytest.mark.parametrize("name", ADDED)
def test_the_added_member_exists(name):
    assert hasattr(W24IdentifierType, name)


@pytest.mark.parametrize("name", ADDED)
def test_the_added_member_value_matches_its_name(name):
    # The caption dimension is `IDENTIFIER/<VALUE>`, so a value that does not
    # equal its member name silently fails to line up with the asset.
    assert W24IdentifierType[name].value == name


def test_project_number_is_distinct_from_project_name():
    # The reason this PR exists: a project's number is not its name, and
    # `PROJECT_NAME` was the only project member, so every `project_number`
    # the reader saw had to go out as a generic number.
    assert W24IdentifierType.PROJECT_NUMBER != W24IdentifierType.PROJECT_NAME
    assert W24IdentifierType.PROJECT_NUMBER.value == "PROJECT_NUMBER"


def test_every_value_is_unique():
    values = [member.value for member in W24IdentifierType]
    assert len(values) == len(set(values))


def test_no_value_has_stray_whitespace_except_the_known_one():
    # `ASSEMBLY_NAME` is the exception and is asserted on its own below. Any
    # NEW one is a typo this catches before it reaches a customer.
    offenders = sorted(
        member.name
        for member in W24IdentifierType
        if member.value != member.value.strip()
    )
    assert offenders == ["ASSEMBLY_NAME"]


def test_the_two_known_misspellings_are_unchanged():
    # Pinned, not endorsed. If either is ever corrected it must be a deliberate
    # change with a migration, and this test is what makes that deliberate.
    assert W24IdentifierType.ITEM_NUMER.value == "ITEM_NUMER"
    assert W24IdentifierType.ASSEMBLY_NAME.value == "ASSEMBLY_NAME "


def test_the_members_are_sorted():
    # The list is maintained alphabetically; an out-of-order insert is how a
    # duplicate slips in unnoticed.
    names = [member.name for member in W24IdentifierType]
    assert names == sorted(names)


def test_it_serialises_as_its_string_value():
    # A `str` Enum, so an existing consumer keeps matching the values it knows
    # and a new member cannot break it.
    assert json.dumps(W24IdentifierType.PROJECT_NUMBER) == '"PROJECT_NUMBER"'
    assert W24IdentifierType.PROJECT_NUMBER == "PROJECT_NUMBER"


def test_a_stakeholder_is_not_an_identifier_type():
    # `OWNER` has a caption dimension too, but it names a party rather than a
    # kind of identifier, which is why it lives here instead.
    assert W24IdentifierStakeholder.OWNER.value == "OWNER"
    assert "OWNER" not in {member.name for member in W24IdentifierType}


def test_the_period_enum_is_untouched():
    assert {member.value for member in W24IdentifierPeriod} == {
        "PREVIOUS",
        "CURRENT",
        "FUTURE",
    }


# ---------------------------------------------------------------------------
# v2
#
# `IdentifierType` in `models/v2/enums.py` is the enum the v2 API returns AND
# the one the public documentation renders: docs-v2's `api-reference/identifier`
# page is `::: werk24.models.v2.models.Identifier`, so the docstring below the
# class IS the published reference. Widening v1 alone would have left the v2
# API unable to express the same kinds, and the docs describing a shorter list
# than either.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("name", ADDED)
def test_the_added_member_exists_in_v2(name):
    assert hasattr(IdentifierType, name)


@pytest.mark.parametrize("name", ADDED)
def test_the_added_v2_member_value_matches_its_name(name):
    assert IdentifierType[name].value == name


def test_the_two_enums_carry_the_same_kinds():
    # Apart from the one member v1 misspells, which v2 corrected.
    v1 = {member.name for member in W24IdentifierType} - _V1_ONLY
    v2 = {member.name for member in IdentifierType} - _V2_ONLY
    assert v1 == v2


def test_v2_corrected_both_v1_misspellings():
    assert IdentifierType.ITEM_NUMBER.value == "ITEM_NUMBER"
    assert IdentifierType.ASSEMBLY_NAME.value == "ASSEMBLY_NAME"


def test_no_v2_value_has_stray_whitespace():
    # v2 has no grandfathered exception, so this one is absolute.
    offenders = sorted(
        member.name
        for member in IdentifierType
        if member.value != member.value.strip()
    )
    assert offenders == []


def test_every_v2_value_is_unique():
    values = [member.value for member in IdentifierType]
    assert len(values) == len(set(values))


def test_the_v2_members_are_sorted():
    names = [member.name for member in IdentifierType]
    assert names == sorted(names)


def test_the_docstring_documents_every_member():
    """The class docstring is the published API reference, so a member missing
    from it is a member missing from the docs.

    This is not hypothetical: before this change the list was nine members
    short of the enum, including `PART_NUMBER` and `PROJECT_NAME`.
    """
    documented = set(re.findall(r"^\s*- ([A-Z][A-Z_]*):", IdentifierType.__doc__, re.M))
    declared = {member.name for member in IdentifierType}
    assert declared - documented == set(), "undocumented members"
    assert documented - declared == set(), "documented members that do not exist"
