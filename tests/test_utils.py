import os
from unittest.mock import mock_open, patch

import pytest

from werk24.utils.license import (
    License,
    LicenseInvalid,
    find_license,
    find_license_in_envs,
    find_license_in_paths,
    parse_license_file,
    parse_license_text,
    save_license_file,
)

# Constants for testing
VALID_LICENSE_TEXT = (
    "W24TECHREAD_AUTH_TOKEN=valid_token\nW24TECHREAD_AUTH_REGION=valid_region\n"
)
INVALID_LICENSE_TEXT = "INVALID_KEY=missing_token\n"


@pytest.fixture
def valid_license():
    """Returns a valid License object."""
    return License(token="valid_token", region="valid_region")  # nosec


@pytest.fixture
def mock_env_vars():
    """Mock valid environment variables."""
    with patch.dict(
        os.environ,
        {
            "W24TECHREAD_AUTH_TOKEN": "valid_token",
            "W24TECHREAD_AUTH_REGION": "valid_region",
        },
    ):
        yield


@pytest.fixture
def mock_search_paths():
    """Mock search paths to avoid creating real files."""
    with patch("werk24.utils.license.SEARCH_PATHS", ["./mock_license.txt"]):
        yield


# Tests
def test_parse_license_text(valid_license):
    """Test parsing valid license text."""
    license = parse_license_text(VALID_LICENSE_TEXT)
    assert license == valid_license  # nosec


def test_parse_license_text_invalid():
    """Test parsing invalid license text raises an exception."""
    with pytest.raises(LicenseInvalid):
        parse_license_text(INVALID_LICENSE_TEXT)


def test_parse_license_file(valid_license, mock_search_paths):
    """Test parsing a valid license file."""
    with patch("builtins.open", mock_open(read_data=VALID_LICENSE_TEXT)):
        license = parse_license_file("./mock_license.txt")
        assert license == valid_license  # nosec


def test_parse_license_file_invalid(mock_search_paths):
    """Test parsing an invalid license file raises an exception."""
    with patch("builtins.open", mock_open(read_data=INVALID_LICENSE_TEXT)):
        with pytest.raises(LicenseInvalid):
            parse_license_file("./mock_license.txt")


def test_find_license_in_paths(mock_search_paths, valid_license):
    """Test finding a license in search paths."""
    with patch("os.path.exists", return_value=True):
        with patch("builtins.open", mock_open(read_data=VALID_LICENSE_TEXT)):
            license = find_license_in_paths()
            assert license == valid_license  # nosec


def test_find_license_in_paths_not_found(mock_search_paths):
    """Test finding a license in paths when no file exists."""
    with patch("builtins.open", side_effect=FileNotFoundError):
        license = find_license_in_paths()
        assert license is None  # nosec


def test_find_license_in_envs(mock_env_vars, valid_license):
    """Test finding a license in environment variables."""
    license = find_license_in_envs()
    assert license == valid_license  # nosec


def test_find_license_in_envs_missing():
    """Test finding a license in envs with missing variables."""
    with patch.dict(os.environ, {}, clear=True):
        license = find_license_in_envs()
        assert license is None  # nosec


def test_find_license_in_paths_and_envs(
    mock_search_paths, mock_env_vars, valid_license
):
    """Test finding a license from paths or environment variables."""
    with patch("builtins.open", mock_open(read_data=VALID_LICENSE_TEXT)):
        license = find_license()
        assert license == valid_license  # nosec


def test_save_license_file(valid_license, mock_search_paths):
    """Test saving a license file."""
    with patch("builtins.open", mock_open()) as mocked_file:
        save_license_file(valid_license)
        mocked_file.assert_called_once_with("./mock_license.txt", "w+")
        mocked_file().write.assert_any_call("W24TECHREAD_AUTH_TOKEN=valid_token\n")
        mocked_file().write.assert_any_call("W24TECHREAD_AUTH_REGION=valid_region\n")


def test_find_license_no_valid_license(mock_search_paths):
    """Test find_license raises exception when no valid license is found."""
    with patch("builtins.open", side_effect=FileNotFoundError), patch.dict(
        os.environ, {}, clear=True
    ):
        with pytest.raises(LicenseInvalid):
            find_license()
