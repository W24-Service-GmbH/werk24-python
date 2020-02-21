import boto3
import hmac
import base64
import hashlib


class CognitoClient:

    def __init__(
            self,
            cognito_region: str,
            cognito_identity_pool_id: str,
            cognito_client_id: str,
            cognito_client_secret: str):

        # store the settings
        self._cognito_region = cognito_region
        self._cognito_identity_pool_id = cognito_identity_pool_id
        self._cognito_client_id = cognito_client_id
        self._cognito_client_secret = cognito_client_secret

        # make empty references to the username and password
        self._username = None
        self._password = None

        # make an empty reference ot the jwt_token
        self.token = None

    def register(self, username: str, password: str) -> None:
        """ Store the username and password locally so
        that it can be used to obtain the token

        Arguments:
            username {str} -- Username
            password {str} -- Password
        """
        self._username = username
        self._password = password

    def _make_cognito_client(self) -> boto3.session.Session.client:
        """ Make the Cognito Client to communicate with
        AWS Cognito

        Returns:
            boto3.session.Session.client -- Boto3 Client
        """
        return boto3.client(
            "cognito-idp",
            self._cognito_region)

    def _make_cognito_secret_hash(self, username: str) -> str:
        """ Make the keyed-hash message authentication code (HMAC) calculated using
        the secret key of a user pool client and username plus the client  ID in the message.

        Arguments:
            username {str} -- Username

        Returns:
            str -- Cognito Secret Hash
        """

        # make the message
        message = username + self._cognito_client_id

        # make the secret
        dig = hmac.new(
            self._cognito_client_secret.encode("UTF-8"),
            msg=message.encode('UTF-8'),
            digestmod=hashlib.sha256).digest()

        # turn the secret into a str object
        return base64.b64encode(dig).decode()

    def login(self):
        """ Login with AWS Cognito
        """

        # make the connection to aws
        cognito_client = self._make_cognito_client()

        # make the authentication data
        auth_data = {
            'USERNAME': self._username,
            'PASSWORD': self._password,
            'SECRET_HASH': self._make_cognito_secret_hash(self._username)}

        # get the jwt token from AWS cognito
        resp = cognito_client.admin_initiate_auth(
            UserPoolId=self._cognito_identity_pool_id,
            AuthFlow='ADMIN_NO_SRP_AUTH',
            AuthParameters=auth_data,
            ClientId=self._cognito_client_id)

        # store the jwt token
        try:
            self.token = resp['AuthenticationResult']['IdToken']
        except KeyError:
            raise RuntimeError(
                "Unable to obtain JWT Token from AWS Cognito.")
