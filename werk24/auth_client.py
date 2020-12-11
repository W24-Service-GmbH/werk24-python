""" Module handling the authentication
"""
import base64
import hashlib
import hmac
from botocore.exceptions import ClientError
from typing import Optional, Tuple

import boto3
from werk24.exceptions import UnauthorizedException


class AuthClient:
    """ Client Module that handles the authentication
    with AWS Cognito.

    Raises:
        UnauthorizedException: Raised when the user credentials are not
            accepted by AWS Cognito

        RuntimeError: Raised when the server behaves in a very unexpected
            way; e.g., when AWS changed the protocol
    """

    def __init__(
            self,
            cognito_region: str,
            cognito_identity_pool_id: str,
            cognito_user_pool_id: str,
            cognito_client_id: str,
            cognito_client_secret: str):

        # store the settings
        self._cognito_region = cognito_region
        self._cognito_identity_pool_id = cognito_identity_pool_id
        self._cognito_user_pool_id = cognito_user_pool_id
        self._cognito_client_id = cognito_client_id
        self._cognito_client_secret = cognito_client_secret

        # make empty references to the username and password
        self.username: Optional[str] = None
        self._password: Optional[str] = None

        # make an empty reference ot the jwt_token
        self.token = None

    def register(self, username: str, password: str) -> None:
        """ Store the username and password locally so
        that it can be used to obtain the token

        Arguments:
            username {str} -- Username
            password {str} -- Password
        """
        self.username = username
        self._password = password

    async def _get_generic_identity(self) -> Tuple[str, str]:
        """ The AWS Cognito User Pools can only be accessed with
        credentials (even if they are generic). This function
        calls the AWS Cognito IDENTITY POOL to obtain the generic
        and unpriviledged credientials

        Raises:
            UnauthorizedException: Raise when we are not able to
                obtain unpriviledged credentials

        Returns:
            Tuple[str, str] -- Access Key, Secret Key Tuple
        """

        # make the identity client
        try:
            identity_client = boto3.client(
                'cognito-identity',
                self._cognito_region)


            # get a new identity id
            identity_response = identity_client.get_id(
                IdentityPoolId=self._cognito_identity_pool_id)
            identity_id = identity_response['IdentityId']

            # obtain the associated credentials
            credentials_response = identity_client \
                .get_credentials_for_identity(IdentityId=identity_id)
            credentials = credentials_response['Credentials']

        except KeyError:
            raise UnauthorizedException("Invalid Cognito configuration")

        except ClientError:  # pylint: disable=try-except-raise
            raise

        # get the access key / secret key
        access_key = credentials.get('AccessKeyId')
        secret_key = credentials.get('SecretKey')
        if access_key is None or secret_key is None:
            raise UnauthorizedException(
                "Unable to obtain Access and Secret Key from "
                "Cognito Identity Pool")

        # that's it
        return access_key, secret_key

    async def _make_cognito_client(self) -> boto3.session.Session.client:
        """ Make the Cognito Client to communicate with
        AWS Cognito

        Returns:
            boto3.session.Session.client -- Boto3 Client
        """

        try:
            # before we can aws cognito USER POOL client, we need
            # to obtain a generic identity from the IDENTIY POOL
            access_key, secret_key = await self._get_generic_identity()

            # with this information, we can now generate the client
            return boto3.client(
                "cognito-idp",
                region_name=self._cognito_region,
                aws_access_key_id=access_key,
                aws_secret_access_key=secret_key)
        except ClientError:
            raise UnauthorizedException("Cognito IDP Client Error")

    def _make_cognito_secret_hash(self, username: str) -> str:
        """ Make the keyed-hash message authentication code (HMAC) calculated
        using the secret key of a user pool client and username plus the client
        ID in the message.

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

    async def login(
        self
    ) -> None:
        """ Login with AWS Cognito

        Raises:
            UnauthorizedException: Raised when the user credentials
                were not accepted by Cognito
        """

        # there is no point in trying to log in if there is no
        # username or password
        if self.username is None or self._password is None:
            raise UnauthorizedException("No username / password provided")

        # make the connection to aws
        cognito_client = await self._make_cognito_client()

        # make the authentication data
        auth_data = {
            'USERNAME': self.username,
            'PASSWORD': self._password,
            'SECRET_HASH': self._make_cognito_secret_hash(self.username)}

        # get the jwt token from AWS cognito
        try:
            resp = cognito_client.initiate_auth(
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters=auth_data,
                ClientId=self._cognito_client_id)

        # We will receive an error message directly from AWS Cognito
        # if anything goes wrong. The error message will be valuable,
        # as it allows the user to differentiate between disabled
        # accounts and incorrect credentials
        except cognito_client.exceptions.NotAuthorizedException:
            raise UnauthorizedException()

        # store the jwt token
        try:
            self.token = resp['AuthenticationResult']['IdToken']
        except KeyError:
            raise UnauthorizedException(
                "Unable to obtain JWT Token from AWS Cognito.")
