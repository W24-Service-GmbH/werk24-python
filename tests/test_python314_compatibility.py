"""Property-based tests for Python 3.14 compatibility.

Feature: python-314-compatibility

This module tests that Pydantic models validate correctly with Python 3.14's
deferred annotation evaluation (PEP 649). The tests verify that:
1. Valid data creates valid model instances
2. Invalid data raises ValidationError
3. Type annotations work correctly with deferred evaluation
"""

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


class TestPydanticModelValidationRejectsInvalidData:
    """Tests that Pydantic models correctly reject invalid data.

    **Validates: Requirements 3.2, 3.3, 6.3**
    """

    @settings(max_examples=100)
    @given(
        invalid_score=st.one_of(
            st.text(min_size=1).filter(
                lambda x: not x.replace(".", "").replace("-", "").isdigit()
            ),
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
            st.text(min_size=1).filter(
                lambda x: not x.replace(".", "").replace("-", "").isdigit()
            ),
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
            st.text(min_size=1).filter(lambda x: not x.isdigit()),
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
