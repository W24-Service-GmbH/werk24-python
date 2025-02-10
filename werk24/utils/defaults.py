from typing import Set

from packaging.version import Version
from pydantic import AnyUrl, Field, HttpUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application configuration settings managed via Pydantic.

    Attributes:
    ----------
    - trial_license_url (HttpUrl): URL to access the trial license.
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

    trial_license_url: HttpUrl = "https://werk24.io/trial-license"
    """URL for obtaining a trial license."""

    http_server: AnyUrl = "https://api.w24.co"
    wss_server: AnyUrl = "wss://ws-api.w24.co/v2"
    """WebSocket server URL for API communication."""

    wss_close_timeout: int = Field(600, gt=0)
    """WebSocket connection close timeout in seconds. Must be greater than 0."""

    max_pages: int = Field(5, gt=0)
    """Maximum number of pages allowed per request. Must be greater than 0."""

    supported_python_versions: Set[Version] = {
        Version("3.9"),
        Version("3.10"),
        Version("3.11"),
        Version("3.12"),
        Version("3.13"),
    }
    """Supported Python versions for compatibility checks."""

    log_level: str = "WARNING"
    """Logging level. Valid values: DEBUG, INFO, WARNING, ERROR, CRITICAL."""

    max_https_retries: int = Field(3, ge=0)
    """Maximum retries for HTTPS requests. Must be greater than or equal to 0."""

    @staticmethod
    def validate_log_level(cls, values):
        """
        Validates the `log_level` attribute.

        Ensures that the log level is one of the accepted values.

        Raises:
        ------
        ValueError:
            If the `log_level` is not in the accepted set.

        Returns:
        -------
        dict:
            The validated values.
        """
        valid_log_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if values.get("log_level") not in valid_log_levels:
            raise ValueError(f"log_level must be one of {valid_log_levels}")
        return values
