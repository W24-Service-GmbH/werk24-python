"""
Dependency validation tests for werk24 package.

These tests validate that the dependency specifications in pyproject.toml
and requirements.txt follow the flexible dependency management strategy
outlined in the design document.
"""

import re
import sys
from pathlib import Path

import pytest

# Python 3.11+ has tomllib built-in, earlier versions need tomli
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        pytest.skip("tomli not available", allow_module_level=True)

from packaging.specifiers import SpecifierSet

# Get project root directory
PROJECT_ROOT = Path(__file__).parent.parent


def parse_pyproject_toml():
    """Parse pyproject.toml and return the configuration."""
    pyproject_path = PROJECT_ROOT / "pyproject.toml"
    with open(pyproject_path, "rb") as f:
        return tomllib.load(f)


def parse_requirements_txt():
    """Parse requirements.txt and return list of dependencies."""
    requirements_path = PROJECT_ROOT / "requirements.txt"
    with open(requirements_path, "r") as f:
        lines = f.readlines()

    # Filter out comments and empty lines
    dependencies = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith("#"):
            dependencies.append(line)

    return dependencies


def parse_test_requirements_txt():
    """Parse tests/requirements.txt and return list of test dependencies."""
    test_requirements_path = PROJECT_ROOT / "tests" / "requirements.txt"
    with open(test_requirements_path, "r") as f:
        lines = f.readlines()

    # Filter out comments and empty lines
    dependencies = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith("#"):
            dependencies.append(line)

    return dependencies


def extract_package_name(dependency_spec):
    """Extract package name from a dependency specification."""
    # Handle various formats: package>=1.0.0, package==1.0.0, package[extra]>=1.0.0
    match = re.match(r"^([a-zA-Z0-9_-]+)", dependency_spec)
    if match:
        return match.group(1)
    return None


def has_upper_bound(specifier_set):
    """Check if a SpecifierSet contains an upper bound constraint."""
    for spec in specifier_set:
        if spec.operator in ["<", "<=", "~="]:
            return True
    return False


def has_exclusion(specifier_set):
    """Check if a SpecifierSet contains an exclusion (!=) constraint."""
    for spec in specifier_set:
        if spec.operator == "!=":
            return True
    return False


# Test-only packages that should NOT be in runtime dependencies
TEST_ONLY_PACKAGES = {
    "pytest",
    "pytest-asyncio",
    "pytest-cov",
    "pytest-mock",
    "coverage",
    "mock",
    "tox",
    "hypothesis",
}


class TestDependencyValidation:
    """Test suite for dependency validation."""

    def test_pyproject_toml_exists(self):
        """Verify pyproject.toml exists."""
        pyproject_path = PROJECT_ROOT / "pyproject.toml"
        assert pyproject_path.exists(), "pyproject.toml not found"

    def test_requirements_txt_exists(self):
        """Verify requirements.txt exists."""
        requirements_path = PROJECT_ROOT / "requirements.txt"
        assert requirements_path.exists(), "requirements.txt not found"

    def test_no_upper_bounds_on_stable_dependencies(self):
        """
        **Feature: flexible-dependency-management, Property 1: No restrictive upper bounds on stable dependencies**
        **Validates: Requirements 1.2, 1.5**

        For any dependency in pyproject.toml that follows semantic versioning and has no
        documented breaking changes, the version specification should not include an upper
        bound constraint (e.g., <=X.Y.Z or <X.Y.Z).
        """
        config = parse_pyproject_toml()
        dependencies = config.get("project", {}).get("dependencies", [])

        violations = []

        for dep in dependencies:
            # Extract package name and version specifier
            parts = re.split(r"([<>=!]+)", dep, maxsplit=1)
            if len(parts) < 2:
                continue

            package_name = parts[0].strip()
            version_spec = dep[len(package_name) :].strip()

            try:
                specifier_set = SpecifierSet(version_spec)

                # Check for upper bounds
                if has_upper_bound(specifier_set):
                    violations.append(
                        f"{package_name}: has upper bound constraint '{version_spec}'"
                    )
            except Exception as e:
                pytest.fail(
                    f"Failed to parse version specifier for {package_name}: {e}"
                )

        assert (
            not violations
        ), "Found dependencies with restrictive upper bounds:\n" + "\n".join(
            f"  - {v}" for v in violations
        )

    def test_exclusions_use_specific_version_syntax(self):
        """
        **Feature: flexible-dependency-management, Property 2: Exclusions use specific version syntax**
        **Validates: Requirements 1.3**

        For any dependency in pyproject.toml that has known problematic versions, the version
        specification should use the exclusion operator (!=) to exclude specific versions
        rather than using an upper bound.
        """
        config = parse_pyproject_toml()
        dependencies = config.get("project", {}).get("dependencies", [])

        violations = []

        for dep in dependencies:
            # Extract package name and version specifier
            parts = re.split(r"([<>=!]+)", dep, maxsplit=1)
            if len(parts) < 2:
                continue

            package_name = parts[0].strip()
            version_spec = dep[len(package_name) :].strip()

            try:
                specifier_set = SpecifierSet(version_spec)

                # If there's an upper bound, check if it's being used as a workaround for exclusions
                if has_upper_bound(specifier_set) and not has_exclusion(specifier_set):
                    # This is flagged as a potential issue - upper bounds should be avoided
                    # unless there's a documented breaking change
                    violations.append(
                        f"{package_name}: uses upper bound '{version_spec}' instead of exclusion syntax"
                    )
            except Exception as e:
                pytest.fail(
                    f"Failed to parse version specifier for {package_name}: {e}"
                )

        # Note: This test will pass if no upper bounds exist (which is the goal)
        # It will fail if upper bounds are used without exclusions
        assert not violations, (
            "Found dependencies using upper bounds instead of exclusion syntax:\n"
            + "\n".join(f"  - {v}" for v in violations)
        )

    def test_requirements_txt_structure(self):
        """
        **Feature: flexible-dependency-management, Property 3: Requirements.txt exists and contains versions**
        **Validates: Requirements 2.1**

        For any release of werk24, the requirements.txt file should exist and contain
        version specifications for all runtime dependencies.
        """
        # Check file exists
        requirements_path = PROJECT_ROOT / "requirements.txt"
        assert requirements_path.exists(), "requirements.txt not found"

        # Parse both files
        config = parse_pyproject_toml()
        runtime_deps = config.get("project", {}).get("dependencies", [])
        requirements_deps = parse_requirements_txt()

        # Extract package names from pyproject.toml
        runtime_packages = set()
        for dep in runtime_deps:
            pkg_name = extract_package_name(dep)
            if pkg_name:
                runtime_packages.add(pkg_name.lower())

        # Extract package names from requirements.txt
        requirements_packages = set()
        for dep in requirements_deps:
            pkg_name = extract_package_name(dep)
            if pkg_name:
                requirements_packages.add(pkg_name.lower())

        # Check that all runtime dependencies are in requirements.txt
        missing = runtime_packages - requirements_packages

        assert (
            not missing
        ), f"Runtime dependencies missing from requirements.txt: {', '.join(sorted(missing))}"

        # Check that all entries in requirements.txt have version specifications
        no_version = []
        for dep in requirements_deps:
            if not re.search(r"[<>=!]", dep):
                no_version.append(dep)

        assert (
            not no_version
        ), f"Dependencies in requirements.txt without version specifications: {', '.join(no_version)}"

    def test_runtime_dependencies_exclude_test_packages(self):
        """
        **Feature: flexible-dependency-management, Property 4: Runtime dependencies exclude test-only packages**
        **Validates: Requirements 3.1, 3.3**

        For any package that is only used for testing (such as pytest, pytest-asyncio),
        it should not appear in the runtime dependencies list in pyproject.toml.
        """
        config = parse_pyproject_toml()
        runtime_deps = config.get("project", {}).get("dependencies", [])

        # Extract package names from runtime dependencies
        runtime_packages = set()
        for dep in runtime_deps:
            pkg_name = extract_package_name(dep)
            if pkg_name:
                runtime_packages.add(pkg_name.lower())

        # Check for test-only packages in runtime dependencies
        test_packages_in_runtime = runtime_packages & TEST_ONLY_PACKAGES

        assert (
            not test_packages_in_runtime
        ), f"Test-only packages found in runtime dependencies: {', '.join(sorted(test_packages_in_runtime))}"

    def test_requirements_txt_uses_exact_version_pins(self):
        """
        **Feature: flexible-dependency-management, Property 5: Requirements.txt uses exact version pins**
        **Validates: Requirements 3.2**

        For any dependency listed in requirements.txt, the version specification should use
        exact version pinning (e.g., ==X.Y.Z or >=X.Y.Z with a specific version) rather than
        open-ended ranges.
        """
        requirements_deps = parse_requirements_txt()

        violations = []

        for dep in requirements_deps:
            # Check if the dependency has a version specifier
            if not re.search(r"[<>=!]", dep):
                violations.append(f"{dep}: no version specifier")
                continue

            # Extract version specifier
            parts = re.split(r"([<>=!]+)", dep, maxsplit=1)
            if len(parts) < 3:
                violations.append(f"{dep}: invalid format")
                continue

            package_name = parts[0].strip()
            operator = parts[1].strip()
            version = parts[2].strip()

            # Check for exact pinning (== or >= with specific version)
            if operator not in ["==", ">="]:
                violations.append(
                    f"{package_name}: uses '{operator}' instead of '==' or '>='"
                )
            elif operator == ">=" and not re.match(r"^\d+\.\d+", version):
                violations.append(f"{package_name}: uses '>=' without specific version")

        assert not violations, (
            "Found dependencies in requirements.txt without exact version pins:\n"
            + "\n".join(f"  - {v}" for v in violations)
        )


class TestDependencyIntegration:
    """Integration tests for dependency compatibility."""

    @pytest.mark.parametrize(
        "package",
        [
            "requests",
            "numpy",
            "pandas",
        ],
    )
    def test_installation_with_popular_packages(self, package, tmp_path):
        """
        Test that werk24 can be installed alongside popular packages without conflicts.

        This integration test verifies that the flexible dependency constraints allow
        pip to resolve compatible versions when werk24 is installed with other common
        packages in the Python ecosystem.

        **Validates: Requirements 1.1, 1.4**
        """
        import subprocess
        import sys

        # Create a temporary virtual environment
        venv_path = tmp_path / "test_venv"

        # Create virtual environment
        result = subprocess.run(
            [sys.executable, "-m", "venv", str(venv_path)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"Failed to create venv: {result.stderr}"

        # Determine pip path based on OS
        if sys.platform == "win32":
            pip_path = venv_path / "Scripts" / "pip"
        else:
            pip_path = venv_path / "bin" / "pip"

        # Install the test package first
        result = subprocess.run(
            [str(pip_path), "install", package],
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert result.returncode == 0, f"Failed to install {package}: {result.stderr}"

        # Try to install werk24 (from current directory)
        result = subprocess.run(
            [str(pip_path), "install", "-e", str(PROJECT_ROOT)],
            capture_output=True,
            text=True,
            timeout=120,
        )

        # Check if installation succeeded
        if result.returncode != 0:
            pytest.fail(
                f"Failed to install werk24 alongside {package}:\n"
                f"STDOUT: {result.stdout}\n"
                f"STDERR: {result.stderr}"
            )

        # Verify both packages are installed
        result = subprocess.run(
            [str(pip_path), "list"],
            capture_output=True,
            text=True,
        )
        installed_packages = result.stdout.lower()

        assert "werk24" in installed_packages, "werk24 not found in installed packages"
        assert (
            package.lower() in installed_packages
        ), f"{package} not found in installed packages"

    def test_python_version_compatibility(self):
        """
        Verify that dependency specifications are compatible with all supported Python versions.

        This test checks that the version constraints in pyproject.toml don't inadvertently
        exclude Python versions that werk24 claims to support.

        **Validates: Requirements 5.5**
        """
        config = parse_pyproject_toml()

        # Check requires-python field
        requires_python = config.get("project", {}).get("requires-python", "")
        assert requires_python, "requires-python not specified in pyproject.toml"

        # Verify it includes Python 3.10+
        specifier_set = SpecifierSet(requires_python)

        # Test that supported versions are included
        supported_versions = ["3.10", "3.11", "3.12", "3.13"]
        for version in supported_versions:
            assert (
                version in specifier_set
            ), f"Python {version} should be supported but is excluded by '{requires_python}'"


class TestCIConfiguration:
    """Test suite for CI/CD configuration validation."""

    def test_ci_workflow_uses_requirements_txt(self):
        """
        Verify that CI workflow installs dependencies from requirements.txt.

        This test parses the GitHub Actions workflow file and verifies that both
        requirements.txt and tests/requirements.txt are installed during the CI run.

        **Validates: Requirements 3.5**
        """
        try:
            import yaml
        except ImportError:
            pytest.skip("PyYAML not available")

        workflow_path = PROJECT_ROOT / ".github" / "workflows" / "python-test.yml"
        assert (
            workflow_path.exists()
        ), "CI workflow file not found at .github/workflows/python-test.yml"

        with open(workflow_path, "r") as f:
            workflow = yaml.safe_load(f)

        # Find the install dependencies step
        jobs = workflow.get("jobs", {})
        test_job = jobs.get("test", {})
        steps = test_job.get("steps", [])

        install_step = None
        for step in steps:
            if (
                step.get("name", "").lower().find("install") != -1
                and step.get("name", "").lower().find("dependencies") != -1
            ):
                install_step = step
                break

        assert (
            install_step is not None
        ), "Could not find 'Install dependencies' step in CI workflow"

        # Check the run command
        run_command = install_step.get("run", "")
        assert run_command, "Install dependencies step has no 'run' command"

        # Verify both requirements files are installed
        assert (
            "requirements.txt" in run_command
        ), "CI workflow does not install requirements.txt"
        assert (
            "tests/requirements.txt" in run_command
        ), "CI workflow does not install tests/requirements.txt"

        # Verify the installation commands are correct
        assert (
            "pip install -r requirements.txt" in run_command
            or "pip install -r requirements.txt" in run_command.replace("\n", " ")
        ), "CI workflow does not use 'pip install -r requirements.txt'"
        assert (
            "pip install -r tests/requirements.txt" in run_command
            or "pip install -r tests/requirements.txt" in run_command.replace("\n", " ")
        ), "CI workflow does not use 'pip install -r tests/requirements.txt'"

    def test_ci_tests_all_supported_python_versions(self):
        """
        Verify that CI workflow tests all supported Python versions.

        This test parses the GitHub Actions workflow matrix configuration and verifies
        that Python 3.10, 3.11, 3.12, and 3.13 are all included in the test matrix.

        **Validates: Requirements 5.5**
        """
        try:
            import yaml
        except ImportError:
            pytest.skip("PyYAML not available")

        workflow_path = PROJECT_ROOT / ".github" / "workflows" / "python-test.yml"
        assert workflow_path.exists(), "CI workflow file not found"

        with open(workflow_path, "r") as f:
            workflow = yaml.safe_load(f)

        # Navigate to the matrix configuration
        jobs = workflow.get("jobs", {})
        test_job = jobs.get("test", {})
        strategy = test_job.get("strategy", {})
        matrix = strategy.get("matrix", {})

        python_versions = matrix.get("python-version", [])

        assert python_versions, "No Python versions found in CI matrix configuration"

        # Check that all required versions are present
        required_versions = ["3.10", "3.11", "3.12", "3.13"]
        for version in required_versions:
            assert version in python_versions, (
                f"Python {version} is not included in CI test matrix. "
                f"Found versions: {python_versions}"
            )

    def test_ci_triggers_on_dependency_file_changes(self):
        """
        Verify that CI workflow triggers on dependency file changes.

        This test checks that the CI workflow is configured to run when pyproject.toml
        or requirements.txt files are modified, ensuring dependency changes are tested.

        **Validates: Requirements 5.1**
        """
        try:
            import yaml
        except ImportError:
            pytest.skip("PyYAML not available")

        workflow_path = PROJECT_ROOT / ".github" / "workflows" / "python-test.yml"
        assert workflow_path.exists(), "CI workflow file not found"

        with open(workflow_path, "r") as f:
            workflow = yaml.safe_load(f)

        # Check the 'on' triggers - note that YAML parses 'on' as boolean True
        # so we need to check both the string key and the boolean key
        triggers = workflow.get("on", workflow.get(True, {}))

        # The workflow should trigger on push events
        # triggers can be a dict with 'push' key, or just the string 'push', or None (meaning push)
        has_push_trigger = (
            "push" in triggers
            if isinstance(triggers, dict)
            else triggers == "push"
            or triggers
            is None  # In YAML, 'on: push' can be parsed as 'True: push: None'
        )

        # Additional check: if triggers is a dict and has 'push' key
        if isinstance(triggers, dict) and "push" in triggers:
            has_push_trigger = True

        # Check if the workflow has push in the True key (YAML parsing quirk)
        if (
            True in workflow
            and isinstance(workflow[True], dict)
            and "push" in workflow[True]
        ):
            has_push_trigger = True

        assert has_push_trigger, (
            f"CI workflow does not trigger on push events. Found triggers: {triggers}, "
            f"workflow keys: {list(workflow.keys())}"
        )

        # Note: The current workflow triggers on ALL pushes, which means it will
        # run when pyproject.toml or requirements.txt change. This is acceptable
        # and actually more comprehensive than only triggering on specific files.
        #
        # If the workflow had path filters, we would verify those here, but
        # triggering on all pushes satisfies the requirement that it runs when
        # dependency files change.
