from typing import Optional
from werk24.techread_client import LicenseError, W24TechreadClient


def make_client(server:Optional[str] = None) -> W24TechreadClient:
    """
    Make the client.

    This will automatically
    fetch the authentication information
    from the environment variables. We will
    provide you with separate .env files for
    the development and production environments

    Returns:
    -------
    W24TechreadClient: Client instance
    """

    server_wss = None if server is None else f"ws-api.{server}"

    try:
        return W24TechreadClient.make_from_env(
            server_wss=server_wss
        )
    except LicenseError as exception:
        print(f"LICENSE ERROR: {exception}")
        raise SystemExit from exception
