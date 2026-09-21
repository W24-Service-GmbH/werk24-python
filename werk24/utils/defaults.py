from typing import ClassVar, Set

from packaging.version import Version
from pydantic import AnyUrl, Field, HttpUrl, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application configuration settings managed via Pydantic.

    Attributes:
    ----------
    - signup_url (HttpUrl): URL to sign up and obtain a license token.
      Default is "https://werk24.io/trial-license".
    - wss_server (AnyUrl): WebSocket server URL for connecting to the Werk24 API.
      Default is "wss://ws-api.w24.co/v2".
    - wss_close_timeout (int): Timeout (in seconds) for WebSocket connections to
      close gracefully. Default is 600 seconds.
    - max_pages (int): Maximum number of pages allowed in a single operation.
      Must be greater than 0. Default is 5.
    - supported_python_versions (Set[Version]): A set of supported Python versions for
      the application. Ensures compatibility checks.
    - log_level (str): Logging level for the application. Acceptable values are: "DEBUG",
      "INFO", "WARNING", "ERROR", "CRITICAL". Default is "INFO".
    - max_https_retries (int): Maximum number of retries for HTTPS requests in case of
      failures. Default is 3, and must be greater than or equal to 0.

    Methods:
    -------
    - validate_log_level(cls, values):
      Ensures that `log_level` is one of the acceptable logging levels.

    """

    signup_url: HttpUrl = "https://werk24.io/trial-license"
    """URL for signing up and obtaining a license token."""

    http_server: AnyUrl = "https://api.w24.co"
    wss_server: AnyUrl = "wss://ws-api.w24.co/v2"
    """WebSocket server URL for API communication."""

    wss_close_timeout: int = Field(600, gt=0)
    """WebSocket connection close timeout in seconds. Must be greater than 0."""

    max_pages: int = Field(5, gt=0)
    """Maximum number of pages allowed per request. Must be greater than 0."""

    supported_python_versions: Set[Version] = {
        Version("3.10"),
        Version("3.11"),
        Version("3.12"),
        Version("3.13"),
        Version("3.14"),
    }
    """Supported Python versions for compatibility checks.

    Kept in sync with ``requires-python`` (>=3.10) and the version classifiers
    in ``pyproject.toml`` (3.10 - 3.14).
    """

    log_level: str = "WARNING"
    """Logging level. Valid values: DEBUG, INFO, WARNING, ERROR, CRITICAL."""

    max_https_retries: int = Field(3, ge=0)
    """Maximum retries for HTTPS requests. Must be greater than or equal to 0.

    Applies to the drawing upload and payload downloads only, and only to 5xx
    and connection errors. A 4xx is never retried: the request is wrong and
    resending it will not make it right. 429 in particular maps to
    ``InsufficientCreditsException``, so retrying it would turn a quota
    refusal into a retry storm against an account that has already run out.
    """

    read_total_timeout: float = Field(180.0, gt=0)
    """Seconds a single ``read_drawing`` may take before it is abandoned.

    The WebSocket keepalive detects a *dead* socket. It cannot detect a live
    socket that will never deliver ``PROGRESS_COMPLETED``, and nothing else
    bounded the wait, so a stalled server hung the caller until
    ``wss_close_timeout`` (600s) - or, for an SDK user, indefinitely.
    """

    read_idle_timeout: float = Field(90.0, gt=0)
    """Seconds to wait for the next message before giving up on a read.

    Shorter than ``read_total_timeout`` because it bounds the gap between
    messages rather than the whole read: a long read still makes progress,
    while a server that has stopped talking is detected without waiting out
    the total.
    """

    VALID_LOG_LEVELS: ClassVar[Set[str]] = {
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    }

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate the ``log_level`` attribute.

        Ensures that the provided log level is one of the accepted values and
        returns the validated value.
        """
        if v not in cls.VALID_LOG_LEVELS:
            raise ValueError(f"log_level must be one of {cls.VALID_LOG_LEVELS}")
        return v
