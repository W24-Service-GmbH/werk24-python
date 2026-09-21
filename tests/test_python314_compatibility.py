"""Property-based tests for Python 3.14 compatibility.

Feature: python-314-compatibility

This module tests that Pydantic models validate correctly with Python 3.14's
deferred annotation evaluation (PEP 649). The tests verify that:
1. Valid data creates valid model instances
2. Invalid data raises ValidationError
3. Type annotations work correctly with deferred evaluation
"""

import decimal
import sys
from decimal import Decimal
from pathlib import Path
from typing import Optional

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import ValidationError

from werk24.models.v2.models import (
    Confidence,
    Quantity,
    Reference,
    Tolerance,
)

# Import models from the werk24 library to test real-world Pydantic models
from werk24.models.v2.status import (
    SystemStatus,
    SystemStatusComponent,
    SystemStatusIncident,
)

# =============================================================================
# Hypothesis Strategies for generating test data
# =============================================================================

# Strategy for generating valid decimal values
decimal_strategy = st.decimals(
    min_value=Decimal("-1000000"),
    max_value=Decimal("1000000"),
    allow_nan=False,
    allow_infinity=False,
)

# Strategy for generating valid confidence scores (0.0 to 1.0)
confidence_score_strategy = st.decimals(
    min_value=Decimal("0"),
    max_value=Decimal("1"),
    allow_nan=False,
    allow_infinity=False,
)

# Strategy for generating valid unit strings
unit_strategy = st.sampled_from(["mm", "cm", "m", "inch", "degree", "radian"])

# Strategy for generating valid status strings
status_strategy = st.sampled_from(
    ["operational", "degraded", "partial_outage", "major_outage"]
)


# =============================================================================
# Property-Based Tests for Pydantic Model Validation
# =============================================================================


class TestPydanticModelValidationWithDeferredAnnotations:
    """Feature: python-314-compatibility, Property 1: Pydantic model validation with deferred annotations

    *For any* valid Pydantic model definition in the werk24-python library,
    instantiating the model with valid data on Python 3.14 SHALL produce a
    correctly validated instance, and instantiating with invalid data SHALL
    raise a ValidationError.

    **Validates: Requirements 3.2, 3.3, 6.3**
    """

    @settings(max_examples=100)
    @given(score=confidence_score_strategy)
    def test_confidence_model_validates_with_valid_data(self, score: Decimal):
        """Test that Confidence model validates correctly with valid decimal scores.

        **Validates: Requirements 3.2, 3.3, 6.3**

        For any valid decimal score between 0 and 1, creating a Confidence
        instance should succeed and preserve the value.
        """
        confidence = Confidence(score=score)
        assert confidence.score == score
        assert isinstance(confidence.score, Decimal)

    @settings(max_examples=100)
    @given(
        value=decimal_strategy,
        unit=unit_strategy,
    )
    def test_quantity_model_validates_with_valid_data(self, value: Decimal, unit: str):
        """Test that Quantity model validates correctly with valid data.

        **Validates: Requirements 3.2, 3.3, 6.3**

        For any valid decimal value and unit string, creating a Quantity
        instance should succeed and preserve the values.
        """
        quantity = Quantity(value=value, unit=unit)
        assert quantity.value == value
        assert quantity.unit == unit

    @settings(max_examples=100)
    @given(reference_id=st.integers(min_value=0, max_value=1000000))
    def test_reference_model_validates_with_valid_data(self, reference_id: int):
        """Test that Reference model validates correctly with valid reference IDs.

        **Validates: Requirements 3.2, 3.3, 6.3**

        For any valid integer reference ID, creating a Reference instance
        should succeed and preserve the value.
        """
        reference = Reference(reference_id=reference_id)
        assert reference.reference_id == reference_id

    @settings(max_examples=100)
    @given(
        tolerance_grade=st.one_of(
            st.none(), st.sampled_from(["IT6", "IT7", "IT8", "IT9"])
        ),
        deviation_lower=st.one_of(st.none(), decimal_strategy),
        deviation_upper=st.one_of(st.none(), decimal_strategy),
        fit=st.one_of(st.none(), st.sampled_from(["H7", "H8", "g6", "h6"])),
        is_theoretically_exact=st.booleans(),
        is_reference=st.booleans(),
        is_general_tolerance=st.booleans(),
        is_approximation=st.booleans(),
    )
    def test_tolerance_model_validates_with_valid_data(
        self,
        tolerance_grade: Optional[str],
        deviation_lower: Optional[Decimal],
        deviation_upper: Optional[Decimal],
        fit: Optional[str],
        is_theoretically_exact: bool,
        is_reference: bool,
        is_general_tolerance: bool,
        is_approximation: bool,
    ):
        """Test that Tolerance model validates correctly with various valid combinations.

        **Validates: Requirements 3.2, 3.3, 6.3**

        For any valid combination of tolerance parameters, creating a Tolerance
        instance should succeed and preserve all values.
        """
        tolerance = Tolerance(
            tolerance_grade=tolerance_grade,
            deviation_lower=deviation_lower,
            deviation_upper=deviation_upper,
            fit=fit,
            is_theoretically_exact=is_theoretically_exact,
            is_reference=is_reference,
            is_general_tolerance=is_general_tolerance,
            is_approximation=is_approximation,
        )
        assert tolerance.tolerance_grade == tolerance_grade
        assert tolerance.deviation_lower == deviation_lower
        assert tolerance.deviation_upper == deviation_upper
        assert tolerance.fit == fit
        assert tolerance.is_theoretically_exact == is_theoretically_exact
        assert tolerance.is_reference == is_reference
        assert tolerance.is_general_tolerance == is_general_tolerance
        assert tolerance.is_approximation == is_approximation

    @settings(max_examples=100)
    @given(
        name=st.text(min_size=1, max_size=100),
        status=status_strategy,
        shortlink=st.one_of(st.none(), st.text(min_size=1, max_size=200)),
    )
    def test_system_status_incident_validates_with_valid_data(
        self, name: str, status: str, shortlink: Optional[str]
    ):
        """Test that SystemStatusIncident model validates correctly.

        **Validates: Requirements 3.2, 3.3, 6.3**

        For any valid incident data, creating a SystemStatusIncident instance
        should succeed and preserve all values.
        """
        incident = SystemStatusIncident(name=name, status=status, shortlink=shortlink)
        assert incident.name == name
        assert incident.status == status
        assert incident.shortlink == shortlink

    @settings(max_examples=100)
    @given(
        id_str=st.text(min_size=1, max_size=50),
        name=st.text(min_size=1, max_size=100),
        status=status_strategy,
    )
    def test_system_status_component_validates_with_valid_data(
        self, id_str: str, name: str, status: str
    ):
        """Test that SystemStatusComponent model validates correctly.

        **Validates: Requirements 3.2, 3.3, 6.3**

        For any valid component data, creating a SystemStatusComponent instance
        should succeed and preserve all values.
        """
        component = SystemStatusComponent(id=id_str, name=name, status=status)
        assert component.id == id_str
        assert component.name == name
        assert component.status == status

    @settings(max_examples=100)
    @given(
        status_indicator=status_strategy,
        page=st.one_of(st.none(), st.text(min_size=1, max_size=200)),
        status_description=st.one_of(st.none(), st.text(min_size=0, max_size=500)),
    )
    def test_system_status_validates_with_valid_data(
        self,
        status_indicator: str,
        page: Optional[str],
        status_description: Optional[str],
    ):
        """Test that SystemStatus model validates correctly with nested models.

        **Validates: Requirements 3.2, 3.3, 6.3**

        For any valid system status data, creating a SystemStatus instance
        should succeed and preserve all values, including empty lists for
        nested models.
        """
        system_status = SystemStatus(
            status_indicator=status_indicator,
            page=page,
            status_description=status_description,
        )
        assert system_status.status_indicator == status_indicator
        assert system_status.page == page
        assert system_status.status_description == status_description
        assert system_status.incidents == []
        assert system_status.scheduled_maintenances == []
        assert system_status.components == []


def _is_not_an_integer(value: str) -> bool:
    """Whether pydantic will refuse *value* for an ``int`` field.

    The filters here used to be ``not value.isdigit()``, which is not the
    same question. ``str.isdigit()`` is False for every negative number, for
    ``"+5"``, for anything with surrounding whitespace and for ``"1_0"`` --
    all of which pydantic accepts -- so hypothesis was free to offer a
    perfectly valid integer as an "invalid" one and the test failed with DID
    NOT RAISE. Issue #572 met that as ``"-0"``.

    Both branches are needed: pydantic's lax mode also takes a float string
    with nothing after the point, so ``"3.0"`` is a valid ``int`` payload
    while ``int("3.0")`` raises.
    """
    try:
        int(value)
        return False
    except ValueError:
        pass
    try:
        return not float(value).is_integer()
    except (ValueError, OverflowError):
        return True


def _is_not_a_decimal(value: str) -> bool:
    """Whether pydantic will refuse *value* for ``Quantity.value``.

    Same defect as ``_is_not_an_integer``, one layer out: the old filter was
    ``not value.replace(".", "").replace("-", "").isdigit()``, which still
    offered ``"+5"``, ``" 1 "`` and ``"1_0"``. It also offered ``"INFINITY"``,
    which is what actually broke a run -- ``Quantity.value`` is declared
    ``allow_inf_nan=True``, so the model was right to accept it and the test
    was wrong to demand a refusal.

    Deciding this with ``Decimal`` itself rather than by inspecting
    characters is the point: the oracle is then the same rule pydantic
    applies, instead of an approximation of it that drifts.
    """
    try:
        decimal.Decimal(value.strip())
        return False
    except (decimal.InvalidOperation, ValueError):
        return True


def _is_not_a_finite_decimal(value: str) -> bool:
    """Whether pydantic will refuse *value* for ``Confidence.score``.

    ``Confidence.score`` is a plain ``Decimal`` and ``Quantity.value`` is a
    ``Decimal`` with ``allow_inf_nan=True``, so the two fields do not accept
    the same set of strings and one shared filter cannot serve both:
    ``Confidence(score="NaN")`` raises ``finite_number`` where
    ``Quantity(value="NaN")`` is fine. Infinities and NaN are therefore
    invalid here and must stay in the strategy.
    """
    if _is_not_a_decimal(value):
        return True
    return not decimal.Decimal(value.strip()).is_finite()


class TestTheInvalidStrategiesAgreeWithTheModels:
    """The filters above must not offer a value the model accepts.

    Without this, a wrong filter only shows up when hypothesis happens to
    generate the offending string -- and then it is replayed from
    ``.hypothesis/`` in that checkout forever while a clean checkout stays
    green, which is how issue #572 presented: "the suite broke on my branch".
    These cases pin the specific strings that broke it, plus the ones the
    old ``isdigit`` filters would have offered for the same reason.
    """

    # Each of these is a valid payload, so the strategies must NOT offer it.
    VALID_INTEGERS = ["-0", "-1", "+5", " 1 ", "1_0", "\n2\t", "3.0", "+3.0"]
    # Accepted by both Decimal fields.
    VALID_DECIMALS = ["-0", "+5", " 1 ", " 2.5 ", "+3.0"]
    # Accepted by Quantity.value (allow_inf_nan=True) but not Confidence.score.
    VALID_FOR_QUANTITY_ONLY = ["INFINITY", "-Infinity", "NaN"]

    @pytest.mark.parametrize("value", VALID_INTEGERS)
    def test_integer_strategy_does_not_offer_a_valid_integer(self, value):
        assert not _is_not_an_integer(value), (
            f"{value!r} would be offered as an invalid reference_id"
        )
        Reference(reference_id=value)

    @pytest.mark.parametrize("value", VALID_DECIMALS)
    def test_decimal_strategy_does_not_offer_a_valid_decimal(self, value):
        assert not _is_not_a_decimal(value), (
            f"{value!r} would be offered as an invalid Quantity.value"
        )
        assert not _is_not_a_finite_decimal(value), (
            f"{value!r} would be offered as an invalid Confidence.score"
        )
        Confidence(score=value)
        Quantity(value=value, unit="mm")

    @pytest.mark.parametrize("value", VALID_FOR_QUANTITY_ONLY)
    def test_the_two_decimal_fields_do_not_share_one_oracle(self, value):
        """allow_inf_nan=True on Quantity.value and not on Confidence.score.

        One filter for both would be wrong in one direction or the other:
        too loose and Quantity's test demands a refusal the model will not
        give, too strict and Confidence's test stops covering inf/NaN.
        """
        assert not _is_not_a_decimal(value)
        assert _is_not_a_finite_decimal(value)
        Quantity(value=value, unit="mm")
        with pytest.raises(ValidationError):
            Confidence(score=value)

    # And the converse: the strategies must still offer genuine rubbish,
    # or the tests they feed would pass vacuously.
    @pytest.mark.parametrize("value", ["", "abc", "1.2.3", "--1", "1e", "0x10"])
    def test_the_strategies_still_offer_genuine_rubbish(self, value):
        assert _is_not_an_integer(value)
        assert _is_not_a_decimal(value)
        assert _is_not_a_finite_decimal(value)
        with pytest.raises(ValidationError):
            Reference(reference_id=value)
        with pytest.raises(ValidationError):
            Confidence(score=value)


class TestPydanticModelValidationRejectsInvalidData:
    """Tests that Pydantic models correctly reject invalid data.

    **Validates: Requirements 3.2, 3.3, 6.3**
    """

    @settings(max_examples=100)
    @given(
        invalid_score=st.one_of(
            st.text(min_size=1).filter(_is_not_a_finite_decimal),
            st.lists(st.integers(), min_size=1),
        )
    )
    def test_confidence_model_rejects_invalid_score_types(self, invalid_score):
        """Test that Confidence model rejects non-decimal score values.

        **Validates: Requirements 3.2, 3.3, 6.3**

        For any value that is not a valid decimal (strings, lists, etc.),
        creating a Confidence instance should raise a ValidationError.
        """
        with pytest.raises(ValidationError):
            Confidence(score=invalid_score)

    @settings(max_examples=100)
    @given(
        invalid_value=st.one_of(
            st.text(min_size=1).filter(_is_not_a_decimal),
            st.lists(st.integers(), min_size=1),
        )
    )
    def test_quantity_model_rejects_invalid_value_types(self, invalid_value):
        """Test that Quantity model rejects non-decimal value types.

        **Validates: Requirements 3.2, 3.3, 6.3**

        For any value that is not a valid decimal, creating a Quantity
        instance should raise a ValidationError.
        """
        with pytest.raises(ValidationError):
            Quantity(value=invalid_value, unit="mm")

    @settings(max_examples=100)
    @given(
        invalid_reference_id=st.one_of(
            st.text(min_size=1).filter(_is_not_an_integer),
            st.floats(allow_nan=True, allow_infinity=True).filter(
                lambda x: (
                    x != int(x) if not (x != x or abs(x) == float("inf")) else True
                )
            ),
        )
    )
    def test_reference_model_rejects_invalid_reference_id_types(
        self, invalid_reference_id
    ):
        """Test that Reference model rejects non-integer reference IDs.

        **Validates: Requirements 3.2, 3.3, 6.3**

        For any value that is not a valid integer (non-numeric strings, floats with decimals),
        creating a Reference instance should raise a ValidationError.
        """
        with pytest.raises(ValidationError):
            Reference(reference_id=invalid_reference_id)

    def test_system_status_rejects_missing_required_field(self):
        """Test that SystemStatus model rejects missing required fields.

        **Validates: Requirements 3.2, 3.3, 6.3**

        Creating a SystemStatus instance without the required status_indicator
        field should raise a ValidationError.
        """
        with pytest.raises(ValidationError):
            SystemStatus()  # Missing required status_indicator


class TestPydanticModelSerializationWithDeferredAnnotations:
    """Tests that Pydantic model serialization works correctly with deferred annotations.

    **Validates: Requirements 3.2, 3.3, 6.3**
    """

    @settings(max_examples=100)
    @given(score=confidence_score_strategy)
    def test_confidence_model_serialization_roundtrip(self, score: Decimal):
        """Test that Confidence model serializes and deserializes correctly.

        **Validates: Requirements 3.2, 3.3, 6.3**

        For any valid Confidence instance, serializing to dict and back
        should preserve the data.
        """
        original = Confidence(score=score)
        serialized = original.model_dump()
        deserialized = Confidence.model_validate(serialized)
        assert deserialized.score == original.score

    @settings(max_examples=100)
    @given(
        value=decimal_strategy,
        unit=unit_strategy,
    )
    def test_quantity_model_serialization_roundtrip(self, value: Decimal, unit: str):
        """Test that Quantity model serializes and deserializes correctly.

        **Validates: Requirements 3.2, 3.3, 6.3**

        For any valid Quantity instance, serializing to dict and back
        should preserve the data.
        """
        original = Quantity(value=value, unit=unit)
        serialized = original.model_dump()
        deserialized = Quantity.model_validate(serialized)
        assert deserialized.value == original.value
        assert deserialized.unit == original.unit

    @settings(max_examples=100)
    @given(
        status_indicator=status_strategy,
        page=st.one_of(st.none(), st.text(min_size=1, max_size=200)),
    )
    def test_system_status_model_serialization_roundtrip(
        self, status_indicator: str, page: Optional[str]
    ):
        """Test that SystemStatus model serializes and deserializes correctly.

        **Validates: Requirements 3.2, 3.3, 6.3**

        For any valid SystemStatus instance, serializing to dict and back
        should preserve the data including nested empty lists.
        """
        original = SystemStatus(status_indicator=status_indicator, page=page)
        serialized = original.model_dump()
        deserialized = SystemStatus.model_validate(serialized)
        assert deserialized.status_indicator == original.status_indicator
        assert deserialized.page == original.page
        assert deserialized.incidents == original.incidents
        assert deserialized.scheduled_maintenances == original.scheduled_maintenances
        assert deserialized.components == original.components


# =============================================================================
# Unit Tests for Configuration Verification
# =============================================================================


class TestConfigurationVerification:
    """Unit tests for verifying Python 3.14 compatibility configuration.

    These tests verify that the configuration files contain the expected
    values for Python 3.14 support.

    _Requirements: 1.1, 2.1, 3.1_
    """

    @pytest.fixture
    def project_root(self) -> Path:
        """Get the project root directory."""
        # tests/test_python314_compatibility.py -> project root
        return Path(__file__).parent.parent

    def test_pyproject_contains_python_314_classifier(self, project_root: Path):
        """Test that pyproject.toml contains Python 3.14 classifier.

        _Requirements: 1.1_

        Verifies that the pyproject.toml file declares Python 3.14 support
        through the appropriate trove classifier.
        """
        pyproject_path = project_root / "pyproject.toml"
        assert pyproject_path.exists(), "pyproject.toml not found"

        with open(pyproject_path, "rb") as f:
            pyproject = tomllib.load(f)

        classifiers = pyproject.get("project", {}).get("classifiers", [])
        assert (
            "Programming Language :: Python :: 3.14" in classifiers
        ), "Python 3.14 classifier not found in pyproject.toml classifiers"

    def test_pyproject_contains_pydantic_version_constraint(self, project_root: Path):
        """Test that pyproject.toml contains pydantic>=2.12.0 constraint.

        _Requirements: 3.1_

        Verifies that the pyproject.toml file specifies pydantic>=2.12.0
        to ensure Python 3.14 compatibility with PEP 649 deferred annotations.
        """
        pyproject_path = project_root / "pyproject.toml"
        assert pyproject_path.exists(), "pyproject.toml not found"

        with open(pyproject_path, "rb") as f:
            pyproject = tomllib.load(f)

        dependencies = pyproject.get("project", {}).get("dependencies", [])

        # Find the pydantic dependency (not pydantic-settings or pydantic-extra-types)
        pydantic_deps = [
            dep
            for dep in dependencies
            if dep.startswith("pydantic>=") and not dep.startswith("pydantic-")
        ]

        assert (
            len(pydantic_deps) == 1
        ), f"Expected exactly one pydantic dependency, found: {pydantic_deps}"

        pydantic_dep = pydantic_deps[0]
        assert (
            ">=2.12.0" in pydantic_dep
        ), f"Expected pydantic>=2.12.0, found: {pydantic_dep}"

    def test_workflow_contains_python_314_in_matrix(self, project_root: Path):
        """Test that workflow file contains Python 3.14 in matrix.

        _Requirements: 2.1_

        Verifies that the GitHub Actions workflow file includes Python 3.14
        in the test matrix.
        """
        import yaml

        workflow_path = project_root / ".github" / "workflows" / "python-test.yml"
        assert workflow_path.exists(), "python-test.yml workflow not found"

        with open(workflow_path, "r") as f:
            workflow = yaml.safe_load(f)

        # Navigate to the python-version matrix
        jobs = workflow.get("jobs", {})
        test_job = jobs.get("test", {})
        strategy = test_job.get("strategy", {})
        matrix = strategy.get("matrix", {})
        python_versions = matrix.get("python-version", [])

        assert (
            "3.14" in python_versions
        ), f"Python 3.14 not found in workflow matrix. Found versions: {python_versions}"
