import io
import os
from typing import Optional

import dotenv
from pydantic import BaseModel

from .logger import get_logger

# Define constants
SEARCH_PATHS = [
    ".werk24",  # Local directory
    os.path.expanduser("~/.werk24"),  # Home directory hidden file
    "werk24_license.txt",  # Current directory license file
    os.path.expanduser("~/werk24_license.txt"),  # Home directory license file
]

# Initialize logger
logger = get_logger()


# Define License Model
class License(BaseModel):
    token: str
    region: str


# Custom exception for invalid licenses
class LicenseInvalid(Exception):
    pass


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
    - LicenseInvalid: If no valid license is found.
    """
    if token is not None and region is not None:
        logger.info("Using provided license token.")
        return License(token=token, region=region)

    logger.info("Searching for a valid license...")
    license = find_license_in_paths() or find_license_in_envs()
    if not license:
        logger.error("No valid license found.")
        raise LicenseInvalid("No valid license could be found.")

    # Overwriting the region if provided
    logger.info("Valid license found.")
    if region is not None:
        logger.warning("Overwriting region with provided value.")
        license.region = region
    return license


def find_license_in_paths() -> Optional[License]:
    """
    Search for a license file in predefined paths.

    Returns:
    -------
    - License: A valid License object if found.
      None: If no valid license is found in the paths.
    """
    for path in SEARCH_PATHS:
        expanded_path = os.path.expanduser(path)
        logger.info(f"Looking for license file at {expanded_path}")
        if os.path.exists(expanded_path):
            try:
                return parse_license_file(expanded_path)
            except LicenseInvalid:
                logger.debug(f"Invalid license at {expanded_path}")
        else:
            logger.debug(f"No license file found at {expanded_path}")
    return None


def find_license_in_envs() -> Optional[License]:
    """
    Search for a license in environment variables.

    Returns:
    -------
    - License: A valid License object if found.
      None: If no valid license is found in the environment variables.
    """
    try:
        token = os.environ["W24TECHREAD_AUTH_TOKEN"]
        region = os.environ["W24TECHREAD_AUTH_REGION"]
        logger.debug("License found in environment variables.")
        return License(token=token, region=region)
    except KeyError:
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
    - LicenseInvalid: If the license file is invalid or cannot be read.
    """
    logger.debug(f"Attempting to parse license file at {path}")
    try:
        with open(path, "r") as file:
            content = file.read()
        return parse_license_text(content)
    except FileNotFoundError as e:
        logger.error(f"License file not found at {path}")
        raise LicenseInvalid("License file not found.") from e
    except Exception as e:
        logger.error(f"Error parsing license file at {path}: {e}")
        raise LicenseInvalid("Invalid license file.") from e


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
    - LicenseInvalid: If the license text is invalid.
    """
    logger.debug("Parsing license text...")
    try:
        vars = {
            k: v for k, v in dotenv.dotenv_values(stream=io.StringIO(text)).items() if v
        }
        token = vars["W24TECHREAD_AUTH_TOKEN"]
        region = vars["W24TECHREAD_AUTH_REGION"]
        logger.debug("License text parsed successfully.")
        return License(token=token, region=region)
    except KeyError as e:
        logger.error(f"Missing key in license text: {e}")
        raise LicenseInvalid("Invalid license text format.") from e


def save_license_file(license: License):
    """
    Save the license to a default file path.

    Args:
    ----
    - license (License): A valid License object to save.
    """
    license_path = os.path.expanduser(SEARCH_PATHS[0])
    try:
        with open(license_path, "w+") as file:
            file.write(f"W24TECHREAD_AUTH_TOKEN={license.token}\n")
            file.write(f"W24TECHREAD_AUTH_REGION={license.region}\n")
        logger.info(f"License saved successfully at {license_path}")
    except Exception as e:
        logger.error(f"Error saving license file: {e}")
        raise LicenseInvalid("Could not save the license file.") from e
