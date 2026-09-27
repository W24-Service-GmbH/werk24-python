import io
import os
from dataclasses import dataclass
from typing import Optional

import dotenv
from pydantic import BaseModel, field_validator

from werk24.utils.exceptions import InvalidLicenseException

from .logger import get_logger

# Define constants
_RAW_SEARCH_PATHS = [
    ".werk24",  # Local directory
    "~/.werk24",  # Home directory hidden file
    "werk24_license.txt",  # Current directory license file
    "~/werk24_license.txt",  # Home directory license file
]

# Expand user paths once at import time
SEARCH_PATHS = [os.path.expanduser(p) for p in _RAW_SEARCH_PATHS]

# Name of the environment variable / dotenv key that holds the auth token.
TOKEN_ENV_KEY = "W24TECHREAD_AUTH_TOKEN"

# Name of the environment variable / dotenv key that holds the (legacy) region.
REGION_ENV_KEY = "W24TECHREAD_AUTH_REGION"

# Only keys at least this long are shown by their last four characters in an
# error message. Below it, four characters are too large a share of the key.
MIN_MASKABLE_TOKEN_LENGTH = 12

# Initialize logger
logger = get_logger()

# License files for which the warning about a different
# W24TECHREAD_AUTH_TOKEN has been logged in this process.
_SHADOW_WARNED: set[str] = set()


# Define License Model
class License(BaseModel):
    token: str

    # The region is a legacy field. Registration now only issues a token, so the
    # region is optional and kept for backwards compatibility with existing
    # license files and environment variables.
    region: Optional[str] = None

    @field_validator("token")
    @classmethod
    def _token_must_not_be_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("The license token must not be empty.")
        return value.strip()


def token_suffix(token: str) -> Optional[str]:
    """
    Return the last four characters of a token, for naming it in a message.

    The console shows the same four characters when it masks a key, so a user
    can match the two. A token shorter than ``MIN_MASKABLE_TOKEN_LENGTH``
    gives None: four characters would be too large a share of it.

    Args:
    ----
    - token (str): The token to describe.

    Returns:
    -------
    - Optional[str]: The last four characters, or None for a short token.
    """
    if len(token) >= MIN_MASKABLE_TOKEN_LENGTH:
        return token[-4:]
    return None


@dataclass(frozen=True)
class LicenseLookup:
    """
    A license together with where it was found.

    Kept apart from ``License`` so that comparing two licenses with ``==``
    still compares only the token and the region.

    Attributes:
    ----------
    - license (License): The license that was found.
    - source (str): "argument", "environment" or "file".
    - path (Optional[str]): The absolute path of the file, when the source is
      "file".
    - env_shadowed (bool): True when the license came from a file while
      ``W24TECHREAD_AUTH_TOKEN`` is set to a different key, which is then
      ignored.
    """

    license: License
    source: str
    path: Optional[str] = None
    env_shadowed: bool = False

    def describe(self) -> str:
        """Say where the key was read from, for a message."""
        if self.source == "argument":
            return "the token argument"
        if self.source == "environment":
            return f"the {TOKEN_ENV_KEY} environment variable"
        return f"the file {self.path}"


def locate_license(
    token: Optional[str] = None, region: Optional[str] = None
) -> LicenseLookup:
    """
    Find a valid license and say where it was found.

    Searches in the same order as ``find_license``: the token argument, then
    the license files in ``SEARCH_PATHS``, then the environment variables.

    Args:
    ----
    - token (str): The license token to use if provided.
    - region (str): The legacy region to use with the token.

    Returns:
    -------
    - LicenseLookup: The license and its source.

    Raises:
    ------
    - InvalidLicenseException: If no valid license is found.
    """

    # -----------------------------------------------------------
    # Check if a token is provided (the region is optional)
    # -----------------------------------------------------------
    if token is not None:
        try:
            return LicenseLookup(License(token=token, region=region), "argument")
        except ValueError as e:
            raise InvalidLicenseException("The license requires a valid token") from e

    # -----------------------------------------------------------
    # If not provided, search for a valid license
    # -----------------------------------------------------------
    logger.info("Searching for a valid license...")
    found = _find_license_file()
    if found is not None:
        license, path = found
        abs_path = os.path.abspath(path)
        env_token = os.environ.get(TOKEN_ENV_KEY, "").strip()
        env_shadowed = bool(env_token) and env_token != license.token
        if env_shadowed and abs_path not in _SHADOW_WARNED:
            _SHADOW_WARNED.add(abs_path)
            logger.warning(
                f"Using the API key in {abs_path}. {TOKEN_ENV_KEY} is also set, "
                "to a different key, and is ignored because license files are "
                f"read first. Correct or delete {abs_path} to use the variable."
            )
        return LicenseLookup(license, "file", abs_path, env_shadowed)

    license = find_license_in_envs()
    if license:
        return LicenseLookup(license, "environment")

    # -----------------------------------------------------------
    # If no valid license is found, raise an exception
    # -----------------------------------------------------------
    logger.error("No valid license found.")
    raise InvalidLicenseException("No valid license could be found.")


def find_license(token: Optional[str] = None, region: Optional[str] = None) -> License:
    """
    Find a valid license by searching predefined paths or environment variables.

    Args:
    ----
    - token (str): The license token to use if provided.

    Returns:
    -------
    - License: A valid License object.

    Raises:
    ------
    - InvalidLicenseException: If no valid license is found.
    """
    return locate_license(token, region).license


def _find_license_file() -> Optional[tuple[License, str]]:
    """
    Search for a license file in predefined paths.

    Returns:
    -------
    - tuple[License, str]: The license and the path it was read from.
      None: If no valid license is found in the paths.
    """
    for path in SEARCH_PATHS:
        logger.info(f"Looking for license file at {path}")
        if os.path.exists(path):
            try:
                return parse_license_file(path), path
            except InvalidLicenseException:
                logger.debug(f"Invalid license at {path}")
        else:
            logger.debug(f"No license file found at {path}")
    return None


def find_license_in_paths() -> Optional[License]:
    """
    Search for a license file in predefined paths.

    Returns:
    -------
    - License: A valid License object if found.
      None: If no valid license is found in the paths.
    """
    found = _find_license_file()
    return found[0] if found is not None else None


def find_license_in_envs() -> Optional[License]:
    """
    Search for a license in environment variables.

    Returns:
    -------
    - License: A valid License object if found.
      None: If no valid license is found in the environment variables.
    """
    token = os.environ.get(TOKEN_ENV_KEY)
    region = os.environ.get(REGION_ENV_KEY)
    if token:
        logger.debug("License found in environment variables.")
        return License(token=token, region=region)
    logger.debug("Required environment variables not set.")
    return None


def parse_license_file(path: str) -> License:
    """
    Parse a license file to extract the license data.

    Args:
    ----
    - path (str): Path to the license file.

    Returns:
    -------
    - License: A valid License object.

    Raises:
    ------
    - InvalidLicenseException: If the license file is invalid or cannot be read.
    """
    logger.debug(f"Attempting to parse license file at {path}")
    try:
        with open(path, "r") as file:
            content = file.read()
        return parse_license_text(content)
    except FileNotFoundError as e:
        logger.error(f"License file not found at {path}")
        raise InvalidLicenseException("License file not found.") from e
    except Exception as e:
        logger.error(f"Error parsing license file at {path}: {e}")
        raise InvalidLicenseException("Invalid license file.") from e


def parse_license_text(text: str) -> License:
    """
    Parse license text and validate its format.

    Two formats are supported:

    1. A dotenv style block containing ``W24TECHREAD_AUTH_TOKEN`` (and
       optionally the legacy ``W24TECHREAD_AUTH_REGION``). This is the format of
       older license files.
    2. A bare token, as issued during registration. In this case the whole
       text is treated as the token.

    Args:
    ----
    - text (str): The content of the license file or the raw token.

    Returns:
    -------
    - License: A valid License object.

    Raises:
    ------
    - InvalidLicenseException: If the license text is invalid.
    """
    logger.debug("Parsing license text...")

    # -----------------------------------------------------------
    # Legacy dotenv format: recognised by the presence of the token key.
    # -----------------------------------------------------------
    if TOKEN_ENV_KEY in text:
        try:
            vars = dotenv.dotenv_values(stream=io.StringIO(text))
            token = vars.get(TOKEN_ENV_KEY)
            region = vars.get(REGION_ENV_KEY)
            if not token:
                raise KeyError("missing token")
            logger.debug("License text parsed successfully (dotenv format).")
            return License(token=token, region=region)
        except (ValueError, KeyError) as e:
            logger.error(f"Missing key in license text: {e}")
            raise InvalidLicenseException("Invalid license text format.") from e

    # -----------------------------------------------------------
    # New format: a bare token, as issued during registration. Use the first
    # non-empty line so trailing whitespace or blank lines from a copy/paste do
    # not break parsing. A line containing "=" is a malformed dotenv block
    # rather than a token, and is rejected.
    # -----------------------------------------------------------
    token = next((line.strip() for line in text.splitlines() if line.strip()), "")
    if not token or "=" in token:
        logger.error("No valid token found in license text.")
        raise InvalidLicenseException("Invalid license text format.")

    logger.debug("License text parsed successfully (bare token).")
    return License(token=token)


def save_license_file(license: License):
    """
    Save the license to a default file path.

    Args:
    ----
    - license (License): A valid License object to save.
    """
    license_path = SEARCH_PATHS[0]
    try:
        # The token is a long-lived bearer credential. Create the file with
        # owner-only permissions (0o600) so other local users cannot read it.
        # os.open with the mode set at creation time avoids a brief window where
        # the file exists with the default (umask-derived, often world-readable)
        # permissions. O_NOFOLLOW (not available on all platforms) refuses to
        # write through a symlink planted at the well-known license path.
        flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
        flags |= getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(license_path, flags, 0o600)
        try:
            file = os.fdopen(fd, "w")
        except Exception:
            os.close(fd)
            raise
        with file:
            file.write(f"{TOKEN_ENV_KEY}={license.token}\n")
            # Only persist the region if one is present (legacy licenses).
            if license.region:
                file.write(f"{REGION_ENV_KEY}={license.region}\n")
        # If the file already existed, os.open does not change its mode, so
        # enforce it explicitly as well.
        os.chmod(license_path, 0o600)
        logger.info(f"License saved successfully at {license_path}")
    except Exception as e:
        logger.error(f"Error saving license file: {e}")
        raise InvalidLicenseException("Could not save the license file.") from e
