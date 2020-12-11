import sys
from werk24.techread_client import LicenseError, W24TechreadClient

def make_client() -> W24TechreadClient:
    """ Make the client. 
    
    This will automatically
    fetch the authentication information
    from the environment variables. We will
    provide you with separate .env files for
    the development and production environments

    Returns:
        W24TechreadClient: Client instance
    """
    
    try:
        return W24TechreadClient.make_from_env()

    # If a license error occured, let the user know.
    # NOTE: This will not catch deactivated users.
    # They will only learn about their status once
    # they send a request.
    except LicenseError as exception:
        print(f"LICENSE ERROR: {exception}")
        sys.exit()