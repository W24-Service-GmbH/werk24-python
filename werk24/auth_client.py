""" Module handling the authentication
"""
from typing import Optional


class AuthClient:
    """Client Module that handles the authentication
    with AWS Cognito.

    Raises:
        UnauthorizedException: Raised when the user credentials are not
            accepted by AWS Cognito

        RuntimeError: Raised when the server behaves in a very unexpected
            way; e.g., when AWS changed the protocol
    """

    def __init__(self, api_token: Optional[str]):
        self.api_token = api_token

    def get_auth_headers(self) -> dict:
        """Get the Authentication Headers.

        There are two authentication methods at the moment.
        You can either go through AWS Cognito or you can
        use the API Token. We will gradually phase out the
        AWS Cognito authentication method. It's too slow
        and too cumbersome.

        Returns:
        -------
        dict: Authentication Headers
        """
        return {"Authorization": "Token " + self.api_token}
    
