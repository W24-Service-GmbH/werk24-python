import io
import os
from dataclasses import dataclass
from typing import Optional

import dotenv
from pydantic import BaseModel, field_validator

from werk24.utils.exceptions import (
    API_TOKENS_URL,
    InvalidLicenseException,
    LicenseNotFoundException,
)

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

# Where ``werk24 init`` saves the token: the home folder, so a script finds it
# whatever folder it is started from. It must stay in SEARCH_PATHS. Every
# earlier release also reads it, so a token saved here works with older client
# versions installed in other environments too.
USER_LICENSE_PATH = os.path.expanduser("~/.werk24")

# Name of the environment variable / dotenv key that holds the auth token.
TOKEN_ENV_KEY = "W24TECHREAD_AUTH_TOKEN"

# Name of the environment variable / dotenv key that holds the (legacy) region.
REGION_ENV_KEY = "W24TECHREAD_AUTH_REGION"

# Characters a token list uses to shorten a token it shows. A token containing one
# of them was copied from such a list, not from where the full token was shown.
_MASK_CHARACTERS = ("\u2022", "\u00b7", "\u2026", "\u25cf", "...", "***")

# How the environment variable is named where the client lists what it checked.
_ENV_LOCATION = f"environment variable {TOKEN_ENV_KEY}"

# Only tokens at least this long are shown by their last four characters in an
# error message. Below it, four characters are too large a share of the token.
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
        # A backstop: the functions that read a token check it first, so they
        # can say why it was refused. A token refused here could never have
        # been accepted by the API.
        problem = token_problem(value)
        if problem:
            raise ValueError(f"The license token is not usable: {problem}.")
        return value.strip()


def token_problem(token: Optional[str]) -> Optional[str]:
    """
    Say why a value cannot be an API token, or return None when it can be.

    Catches what a paste most often gets wrong: an empty value, the
    shortened token a token list shows (for example ``wk24_\u2022\u2022\u2022\u2022wxyz``),
    a prefix such as ``Token``, and characters that cannot be sent in an
    HTTP header at all. It does not say whether the API accepts the token;
    only the API can.

    Args:
    ----
    - token (Optional[str]): The value to check. Surrounding whitespace is
      ignored.

    Returns:
    -------
    - Optional[str]: The reason, in lower case without a trailing period,
      or None when the value may be a token.
    """
    value = (token or "").strip()
    if not value:
        return "it is empty"
    if any(mark in value for mark in _MASK_CHARACTERS):
        return "it looks like the shortened token shown in a token list, not the full token"
    if any(character.isspace() for character in value):
        return (
            "it contains spaces; use the token on its own, without a prefix "
            "such as 'Token'"
        )
    if not value.isascii() or not value.isprintable():
        return "it contains characters that never appear in an API token"
    return None


def token_suffix(token: str) -> Optional[str]:
    """
    Return the last four characters of a token, for naming it in a message.

    The console shows the same four characters when it masks a token, so a user
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
      ``W24TECHREAD_AUTH_TOKEN`` is set to a different token, which is then
      ignored.
    """

    license: License
    source: str
    path: Optional[str] = None
    env_shadowed: bool = False

    def describe(self) -> str:
        """Say where the token was read from, for a message."""
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
    A file or variable that holds something that cannot be a token is skipped
    with a WARNING that says why, and the search goes on.

    Args:
    ----
    - token (str): The license token to use if provided.
    - region (str): The legacy region to use with the token.

    Returns:
    -------
    - LicenseLookup: The license and its source.

    Raises:
    ------
    - InvalidLicenseException: If the token argument cannot be an API token.
    - LicenseNotFoundException: If no valid license is found. A subclass of
      InvalidLicenseException; its message lists every place the client
      looked and what it found there.
    """

    # -----------------------------------------------------------
    # Check if a token is provided (the region is optional). A token passed
    # explicitly is used as is; nothing else is searched.
    # -----------------------------------------------------------
    if token is not None:
        problem = token_problem(token)
        if problem:
            raise InvalidLicenseException(
                f"The token passed to Werk24Client is not usable: {problem}."
            )
        try:
            return LicenseLookup(License(token=token, region=region), "argument")
        except ValueError as e:
            raise InvalidLicenseException("The license requires a valid token") from e

    # -----------------------------------------------------------
    # If not provided, search for a valid license
    # -----------------------------------------------------------
    logger.info("Searching for a valid license...")
    searched: list[tuple[str, str]] = []
    seen: set[str] = set()
    for path in SEARCH_PATHS:
        abs_path = os.path.abspath(path)
        # In the home folder, ".werk24" and "~/.werk24" are the same file.
        if abs_path in seen:
            continue
        seen.add(abs_path)

        license, outcome = _check_license_file(path)
        if license is None:
            searched.append((abs_path, outcome))
            continue

        env_token = os.environ.get(TOKEN_ENV_KEY, "").strip()
        env_shadowed = bool(env_token) and env_token != license.token
        if env_shadowed and abs_path not in _SHADOW_WARNED:
            _SHADOW_WARNED.add(abs_path)
            logger.warning(
                f"Using the API token in {abs_path}. {TOKEN_ENV_KEY} is also set, "
                "to a different token, and is ignored because license files are "
                f"read first. Correct or delete {abs_path} to use the variable."
            )
        return LicenseLookup(license, "file", abs_path, env_shadowed)

    license, outcome = _check_license_env()
    if license is not None:
        return LicenseLookup(license, "environment")
    searched.append((_ENV_LOCATION, outcome))

    # -----------------------------------------------------------
    # If no valid license is found, raise an exception. It carries the
    # explanation, so the log line stays at INFO.
    # -----------------------------------------------------------
    logger.info("No valid license found.")
    save_path = USER_LICENSE_PATH
    raise LicenseNotFoundException(
        searched,
        save_path=None if save_path.startswith("~") else os.path.abspath(save_path),
        tokens_url=API_TOKENS_URL,
    )


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
    - InvalidLicenseException: If no valid license is found. When none is
      configured at all, this is LicenseNotFoundException.
    """
    return locate_license(token, region).license


#: ``find_license`` as defined above. ``Werk24Client`` compares the name it
#: would call against this one. When they differ, a caller replaced it (for
#: example a test patching ``werk24.techread.find_license``), and the client
#: calls the replacement instead of searching for a token itself.
_ORIGINAL_FIND_LICENSE = find_license


def _check_license_file(path: str) -> tuple[Optional[License], str]:
    """
    Read one license file.

    Args:
    ----
    - path (str): The path to read.

    Returns:
    -------
    - tuple[Optional[License], str]: The license, or None with what was
      found instead ("not found", or why the file cannot be used).
    """
    logger.info(f"Looking for license file at {path}")
    if not os.path.exists(path):
        logger.debug(f"No license file found at {path}")
        return None, "not found"
    try:
        return parse_license_file(path), "found"
    except InvalidLicenseException as e:
        abs_path = os.path.abspath(path)
        logger.warning(f"Skipping the license file {abs_path}: {e.reason}.")
        return None, f"found, but not usable: {e.reason}"


def _check_license_env() -> tuple[Optional[License], str]:
    """
    Read the license from the environment variables.

    Returns:
    -------
    - tuple[Optional[License], str]: The license, or None with what was
      found instead ("not set", or why the value cannot be used).
    """
    token = os.environ.get(TOKEN_ENV_KEY)
    if token is None:
        logger.debug("Required environment variables not set.")
        return None, "not set"

    problem = token_problem(token)
    if problem is None:
        try:
            license = License(token=token, region=os.environ.get(REGION_ENV_KEY))
        except ValueError:
            problem = "it could not be parsed"
        else:
            logger.debug("License found in environment variables.")
            return license, "found"

    # Never log the value itself: it may be a working token with a typo.
    logger.warning(f"Ignoring the environment variable {TOKEN_ENV_KEY}: {problem}.")
    return None, f"set, but not usable: {problem}"


def find_license_in_paths() -> Optional[License]:
    """
    Search for a license file in predefined paths.

    ``find_license`` and ``Werk24Client`` no longer call this function; they
    go through ``locate_license``, which also records where the token was
    found. Replacing this function therefore does not change which token the
    client uses. To give a client a token in a test, patch
    ``werk24.techread.find_license`` or pass ``token=`` to ``Werk24Client``.

    Returns:
    -------
    - License: A valid License object if found.
      None: If no valid license is found in the paths.
    """
    for path in SEARCH_PATHS:
        license, _ = _check_license_file(path)
        if license is not None:
            return license
    return None


def find_license_in_envs() -> Optional[License]:
    """
    Search for a license in environment variables.

    ``find_license`` and ``Werk24Client`` no longer call this function; they
    go through ``locate_license``, which also records where the token was
    found. Replacing this function therefore does not change which token the
    client uses. To give a client a token in a test, patch
    ``werk24.techread.find_license`` or pass ``token=`` to ``Werk24Client``.

    Returns:
    -------
    - License: A valid License object if found.
      None: If the variable is not set, or holds something that cannot be a
      token (logged as a WARNING).
    """
    license, _ = _check_license_env()
    return license


def parse_license_file(path: str) -> License:
    """
    Parse a license file to extract the license data.

    Args:
    ----
    - path (str): Path to the license file. A leading ``~`` is expanded to
      the home folder.

    Returns:
    -------
    - License: A valid License object.

    Raises:
    ------
    - InvalidLicenseException: If the license file is invalid or cannot be
      read. Its ``reason`` says which.
    """
    # A path such as "~/.werk24" names the home folder, as it does in a shell.
    path = os.path.expanduser(path)
    logger.debug(f"Attempting to parse license file at {path}")
    try:
        # utf-8-sig also reads a file an editor saved with a byte order mark.
        with open(path, "r", encoding="utf-8-sig") as file:
            content = file.read()
    except FileNotFoundError as e:
        logger.debug(f"License file not found at {path}")
        raise InvalidLicenseException("not found") from e
    except UnicodeDecodeError as e:
        logger.debug(f"License file at {path} is not a text file")
        raise InvalidLicenseException("it is not a text file") from e
    except OSError as e:
        logger.debug(f"License file at {path} could not be read: {e}")
        raise InvalidLicenseException(
            f"it could not be read ({type(e).__name__})"
        ) from e

    try:
        return parse_license_text(content)
    except InvalidLicenseException:
        raise
    except Exception as e:
        logger.debug(f"Error parsing license file at {path}: {type(e).__name__}")
        raise InvalidLicenseException("it could not be parsed") from e


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
    - InvalidLicenseException: If the license text is invalid. Its
      ``reason`` says why, without repeating the text.
    """
    logger.debug("Parsing license text...")

    # -----------------------------------------------------------
    # Legacy dotenv format: recognised by the presence of the token key.
    # -----------------------------------------------------------
    if TOKEN_ENV_KEY in text:
        try:
            vars = dotenv.dotenv_values(stream=io.StringIO(text))
        except ValueError as e:
            raise InvalidLicenseException("it could not be parsed") from e
        token = vars.get(TOKEN_ENV_KEY)
        region = vars.get(REGION_ENV_KEY)
        if not token or not token.strip():
            logger.debug("No token found in the license text (dotenv format).")
            raise InvalidLicenseException(f"it has no value for {TOKEN_ENV_KEY}")
        license = _make_license(token, region)
        logger.debug("License text parsed successfully (dotenv format).")
        return license

    # -----------------------------------------------------------
    # New format: a bare token, as issued during registration. Use the first
    # non-empty line so trailing whitespace or blank lines from a copy/paste do
    # not break parsing. A line containing "=" is a malformed dotenv block
    # rather than a token, and is rejected.
    # -----------------------------------------------------------
    token = next((line.strip() for line in text.splitlines() if line.strip()), "")
    if "=" in token:
        logger.debug("The license text is not a token.")
        raise InvalidLicenseException("it is not an API token")

    license = _make_license(token, None)
    logger.debug("License text parsed successfully (bare token).")
    return license


def _make_license(token: str, region: Optional[str]) -> License:
    """
    Build a License, raising InvalidLicenseException with the reason.

    Args:
    ----
    - token (str): The token read from a file or a paste.
    - region (Optional[str]): The legacy region, if any.

    Returns:
    -------
    - License: A valid License object.

    Raises:
    ------
    - InvalidLicenseException: If the value cannot be an API token.
    """
    problem = token_problem(token)
    if problem:
        logger.debug(f"The license text holds no usable token: {problem}.")
        raise InvalidLicenseException(problem)
    try:
        return License(token=token, region=region)
    except ValueError as e:
        # pydantic's ValidationError is a ValueError. Never let it escape: the
        # callers only expect InvalidLicenseException.
        raise InvalidLicenseException("it could not be parsed") from e


def save_license_file(license: License, path: Optional[str] = None) -> str:
    """
    Save the license to a file, readable only by the current user.

    Args:
    ----
    - license (License): A valid License object to save.
    - path (Optional[str]): Where to save it. Defaults to ``.werk24`` in
      the current working folder (the first of ``SEARCH_PATHS``), as in
      earlier releases. ``werk24 init`` passes ``USER_LICENSE_PATH``
      (``~/.werk24``) instead, where the client finds it from any folder.
      A leading ``~`` is expanded to the home folder.

    Returns:
    -------
    - str: The absolute path the license was saved to.

    Raises:
    ------
    - InvalidLicenseException: If the file cannot be written. Its ``reason``
      names the path.
    """
    # Read the module global at call time, not as a default argument, so it
    # can be changed after import. A path such as "~/.werk24" names the home
    # folder, as it does in a shell.
    license_path = os.path.expanduser(path if path is not None else SEARCH_PATHS[0])
    if license_path.startswith("~"):
        # expanduser leaves the path unchanged when it cannot find the home
        # folder. Writing it as is would create a folder named "~".
        raise InvalidLicenseException(
            "could not find your home folder to save the token in; set the "
            f"environment variable {TOKEN_ENV_KEY} instead"
        )
    abs_path = os.path.abspath(license_path)
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
        logger.info(f"License saved successfully at {abs_path}")
    except Exception as e:
        logger.error(f"Error saving license file: {e}")
        raise InvalidLicenseException(
            f"could not save the token to {abs_path}: {e}"
        ) from e
    return abs_path
