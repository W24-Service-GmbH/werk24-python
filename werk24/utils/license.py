import io
import os
from typing import Optional

import dotenv
from pydantic import BaseModel

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

# Initialize logger
logger = get_logger()


# Define License Model
class License(BaseModel):
    token: str
    region: str


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
    # Check if token and region are provided
    # -----------------------------------------------------------
    if token is not None:
        try:
            return License(token=token, region=region)
        except ValueError as e:
            raise InvalidLicenseException(
                "The license requires a token and a region"
            ) from e

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
    token = os.environ.get("W24TECHREAD_AUTH_TOKEN")
    region = os.environ.get("W24TECHREAD_AUTH_REGION")
    if token and region:
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

    Args:
    ----
    - text (str): The content of the license file.

    Returns:
    -------
    - License: A valid License object.

    Raises:
    ------
    - InvalidLicenseException: If the license text is invalid.
    """
    logger.debug("Parsing license text...")
    try:
        vars = dotenv.dotenv_values(stream=io.StringIO(text))
        token = vars.get("W24TECHREAD_AUTH_TOKEN")
        region = vars.get("W24TECHREAD_AUTH_REGION")
        if not (token and region):
            raise KeyError("missing token or region")
        logger.debug("License text parsed successfully.")
        return License(token=token, region=region)
    except (ValueError, KeyError) as e:
        logger.error(f"Missing key in license text: {e}")
        raise InvalidLicenseException("Invalid license text format.") from e


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
            file.write(f"W24TECHREAD_AUTH_TOKEN={license.token}\n")
            file.write(f"W24TECHREAD_AUTH_REGION={license.region}\n")
        logger.info(f"License saved successfully at {license_path}")
    except Exception as e:
        logger.error(f"Error saving license file: {e}")
        raise InvalidLicenseException("Could not save the license file.") from e
