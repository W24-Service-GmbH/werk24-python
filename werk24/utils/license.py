import io
import os
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

# Initialize logger
logger = get_logger()


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

    # -----------------------------------------------------------
    # Check if a token is provided (the region is optional)
    # -----------------------------------------------------------
    if token is not None:
        try:
            return License(token=token, region=region)
        except ValueError as e:
            raise InvalidLicenseException("The license requires a valid token") from e

    # -----------------------------------------------------------
    # If not provided, search for a valid license
    # -----------------------------------------------------------
    logger.info("Searching for a valid license...")
    license = find_license_in_paths() or find_license_in_envs()
    if license:
        return license

    # -----------------------------------------------------------
    # If no valid license is found, raise an exception
    # -----------------------------------------------------------
    logger.error("No valid license found.")
    raise InvalidLicenseException("No valid license could be found.")


def find_license_in_paths() -> Optional[License]:
    """
    Search for a license file in predefined paths.

    Returns:
    -------
    - License: A valid License object if found.
      None: If no valid license is found in the paths.
    """
    for path in SEARCH_PATHS:
        logger.info(f"Looking for license file at {path}")
        if os.path.exists(path):
            try:
                return parse_license_file(path)
            except InvalidLicenseException:
                logger.debug(f"Invalid license at {path}")
        else:
            logger.debug(f"No license file found at {path}")
    return None


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
        with open(license_path, "w+") as file:
            file.write(f"{TOKEN_ENV_KEY}={license.token}\n")
            # Only persist the region if one is present (legacy licenses).
            if license.region:
                file.write(f"{REGION_ENV_KEY}={license.region}\n")
        logger.info(f"License saved successfully at {license_path}")
    except Exception as e:
        logger.error(f"Error saving license file: {e}")
        raise InvalidLicenseException("Could not save the license file.") from e
