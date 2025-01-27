from packaging.version import Version
from pydantic import AnyUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    trial_license_url: str = "https://werk24.io/trial-license"

    wss_server: AnyUrl = "wss://ws-api.w24.co/v2"
    wss_close_timeout: int = 600

    max_pages: int = 5

    supported_python_versions: list[Version] = [
        Version("3.9"),
        Version("3.10"),
        Version("3.11"),
        Version("3.12"),
        Version("3.13"),
    ]

    log_level: str = "INFO"

    max_https_retries: int = 3
