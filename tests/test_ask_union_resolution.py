"""An ask must come back out of ``AskUnion`` as the class that went in.

``AskUnion`` is an ordinary ``Union``, so pydantic tries its members and takes
the first that validates. Two things made that resolve to the wrong class:

- Every concrete v1 ask declared ``ask_type: W24AskType = <its own type>``.
  The annotation is the whole enum, not a ``Literal``, so each class accepted
  every ask type rather than only its own. The v2 asks never had this -- they
  have always been ``Literal`` -- and ``W24AskTitleBlock`` was the one v1 class
  that did too.
- ``W24AskThumbnail`` was a member. It is a base, not an ask: it inherits the
  required, unconstrained ``ask_type`` from ``W24Ask`` and defaults its own two
  fields, so it matches literally any v1 ask, and it sits ahead of most of them.

The result was that 17 of the 28 v1 asks could not survive a round-trip.
``{"version": "v1", "ask_type": "PRODUCT_PMI_EXTRACT"}`` came back as a
``W24AskThumbnail`` carrying a fabricated ``file_format: JPEG`` and
``balloons: []``, and those invented fields were then persisted into
``crew-api-request`` and into ``ask_details`` on the request log.

Nothing lost a value, because ``W24AskThumbnail`` happens to be a permissive
superset of the asks it swallowed. That is luck, not design: an ask given a
field the base does not have would have had it silently dropped.
"""

import pytest
from pydantic import TypeAdapter, ValidationError

from werk24 import AskUnion
from werk24.models.v1.ask import (
    W24Ask,
    W24AskNotes,
    W24AskProductPMIExtract,
    W24AskThumbnail,
    W24AskType,
    W24AskVariantProcesses,
)
from werk24.models.v2.asks import AskV2, get_ask_subclasses

ADAPTER = TypeAdapter(list[AskUnion])
MEMBERS = get_ask_subclasses()


def _resolve(raw):
    """Validate a single ask dict through the union."""
    return ADAPTER.validate_python([raw])[0]


def _default_constructible():
    """Union members that can be built with no arguments.

    A couple of asks require a field, and those are exercised by name below
    rather than skipped silently.
    """
    for cls in MEMBERS:
        try:
            yield pytest.param(cls(), id=cls.__name__)
        except ValidationError:
            continue


class TestEveryAskResolvesToItself:
    """The property the union exists to provide."""

    @pytest.mark.parametrize("ask", list(_default_constructible()))
    def test_round_trip_preserves_the_class(self, ask):
        assert type(_resolve(ask.model_dump(mode="json"))) is type(ask)

    @pytest.mark.parametrize("ask", list(_default_constructible()))
    def test_round_trip_invents_no_fields(self, ask):
        raw = ask.model_dump(mode="json")
        assert _resolve(raw).model_dump(mode="json") == raw


class TestTheSpecificAsksThatWereWrong:
    """The three Laserhub sends, and the shape they arrive in."""

    @pytest.mark.parametrize(
        "ask_type,expected",
        [
            ("PRODUCT_PMI_EXTRACT", W24AskProductPMIExtract),
            ("VARIANT_PROCESSES", W24AskVariantProcesses),
            ("NOTES", W24AskNotes),
        ],
    )
    def test_a_bare_v1_ask_is_its_own_class(self, ask_type, expected):
        raw = {"version": "v1", "ask_type": ask_type, "is_training": False}
        assert type(_resolve(raw)) is expected

    @pytest.mark.parametrize(
        "ask_type", ["PRODUCT_PMI_EXTRACT", "VARIANT_PROCESSES", "NOTES"]
    )
    def test_no_thumbnail_fields_are_attached(self, ask_type):
        raw = {"version": "v1", "ask_type": ask_type, "is_training": False}
        resolved = _resolve(raw).model_dump(mode="json")
        assert "file_format" not in resolved
        assert "balloons" not in resolved

    def test_the_version_key_does_not_decide_the_class(self):
        """Laserhub sends ``ask_version`` on a v1 ask, which is not the field.

        v1 asks key off ``version`` and v2 off ``ask_version``. The wrong one
        is an unknown key, ignored, and ``ask_type`` alone still has to land
        the ask on its own class.
        """
        raw = {"ask_version": "v1", "ask_type": "VARIANT_PROCESSES"}
        assert type(_resolve(raw)) is W24AskVariantProcesses


class TestTheInvariantsThatMakeResolutionUnambiguous:
    def test_the_thumbnail_base_is_not_a_member(self):
        assert W24AskThumbnail not in MEMBERS

    def test_every_member_names_its_own_ask_type(self):
        """A member that does not is a base, and would match everything."""
        for cls in MEMBERS:
            field = cls.model_fields.get("ask_type")
            assert field is not None, cls.__name__
            assert not field.is_required(), cls.__name__

    def test_no_two_members_claim_the_same_ask_type(self):
        seen = {}
        for cls in MEMBERS:
            value = cls.model_fields["ask_type"].default
            value = getattr(value, "value", value)
            assert value not in seen, f"{cls.__name__} collides with {seen.get(value)}"
            seen[value] = cls.__name__

    def test_every_v1_member_constrains_ask_type_to_a_literal(self):
        """The bare enum annotation is what let each class accept any type."""
        for cls in MEMBERS:
            if issubclass(cls, AskV2):
                continue
            annotation = cls.model_fields["ask_type"].annotation
            assert annotation is not W24AskType, (
                f"{cls.__name__} still annotates ask_type as the whole enum"
            )

    def test_the_union_still_covers_every_ask_type(self):
        """Excluding bases must not drop an ask type from the union."""
        covered = {
            getattr(c.model_fields["ask_type"].default, "value", None)
            for c in MEMBERS
            if not issubclass(c, AskV2)
        }
        missing = {t.value for t in W24AskType} - covered
        # VARIANT_TOLERANCE_ELEMENTS is declared in the enum with no ask class
        # of its own; it was never in the union and is not added here.
        assert missing <= {"VARIANT_TOLERANCE_ELEMENTS"}, missing


class TestCompatibilityWithWhatIsAlreadyStored:
    """Rows written while the union was picking the wrong class."""

    @pytest.mark.parametrize(
        "ask_type,expected",
        [
            ("PRODUCT_PMI_EXTRACT", W24AskProductPMIExtract),
            ("NOTES", W24AskNotes),
        ],
    )
    def test_a_stored_row_still_loads_and_is_cleaned_up(self, ask_type, expected):
        stored = {
            "version": "v1",
            "ask_type": ask_type,
            "is_training": False,
            "file_format": "JPEG",
            "balloons": [],
        }
        resolved = _resolve(stored)
        assert type(resolved) is expected
        assert "file_format" not in resolved.model_dump(mode="json")

    def test_a_real_thumbnail_ask_keeps_its_format(self):
        """The fields are only spurious on asks that never had them."""
        raw = {"version": "v1", "ask_type": "PAGE_THUMBNAIL", "file_format": "PNG"}
        resolved = _resolve(raw)
        assert resolved.ask_type is W24AskType.PAGE_THUMBNAIL
        assert resolved.file_format.value == "PNG"

    def test_an_unknown_ask_type_is_still_refused(self):
        with pytest.raises(ValidationError):
            _resolve({"version": "v1", "ask_type": "NOT_A_REAL_ASK"})


class TestAsksThatCarryParameters:
    """These resolved correctly before, because their fields disambiguated them.

    They are the reason nothing was lost in practice, and the reason this was
    a trap rather than an outage. They must keep working.
    """

    @pytest.mark.parametrize(
        "raw,field,value",
        [
            ({"version": "v1", "ask_type": "VARIANT_CAD", "output_format": "DXF"},
             "output_format", "DXF"),
            ({"version": "v1", "ask_type": "DEBUG", "debug_key": "k"},
             "debug_key", "k"),
        ],
    )
    def test_parameters_survive(self, raw, field, value):
        resolved = _resolve(raw)
        got = getattr(resolved, field)
        assert getattr(got, "value", got) == value


def test_the_base_class_is_still_usable_for_subclassing():
    """Leaving it out of the union must not make it unimportable."""
    assert issubclass(W24AskThumbnail, W24Ask)
    assert "file_format" in W24AskThumbnail.model_fields
