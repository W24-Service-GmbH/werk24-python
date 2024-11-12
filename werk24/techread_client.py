""" W24Client Module

DESCRIPTION
    The module contains everything that is needed to
    communicate with the W24 API - allowing you
    to interpret the contents of your technical drawings.

AUTHOR
    Jochen Mattes (Werk24)

EXAMPLE
    # obtain the thumbnail of a page
    drawing_bytes = open(...,"r").read()
    client = W24TechreadClient.make_from_env()
    await client.read_drawing_with_hooks(
        drawing_bytes,
        [Hook(
                ask=W24AskPageThumbnail(),
                function=lambda msg: print("Received Thumbnail of Page")
        ]))
"""
import asyncio
import json
from werk24.crypt import (
    generate_new_key_pair,
    decrypt_with_private_key,
    encrypt_with_public_key,
)
import logging
from io import BufferedReader
import os
from typing import Any
import uuid
from asyncio import iscoroutinefunction
from types import TracebackType
from typing import (
    AsyncGenerator,
    AsyncIterator,
    Callable,
    Dict,
    List,
    Optional,
    Type,
    Union,
    Tuple,
)
from werk24.auth_client import AuthClient

import dotenv
from pydantic import UUID4, BaseModel

from werk24.exceptions import (
    BadRequestException,
    LicenseError,
    RequestTooLargeException,
    ServerException,
    UnsupportedMediaType,
    InsufficientCreditsException
)
from werk24.models.ask import W24Ask
from werk24.models.helpdesk import W24HelpdeskTask
from werk24.models.techread import (
    W24TechreadAction,
    W24TechreadException,
    W24TechreadExceptionLevel,
    W24TechreadExceptionType,
    W24TechreadInitResponse,
    W24TechreadMessage,
    W24TechreadMessageSubtype,
    W24TechreadMessageType,
    W24TechreadRequest,
)
from werk24.techread_client_https import TechreadClientHttps
from werk24.techread_client_wss import TechreadClientWss

# make the logger
logger = logging.getLogger("w24_techread_client")


EXCEPTION_MAP = {
    RequestTooLargeException: W24TechreadExceptionType.DRAWING_FILE_SIZE_TOO_LARGE,
    BadRequestException: W24TechreadExceptionType.DRAWING_FILE_SIZE_TOO_LARGE,
}
""" Map to translate the local exceptions to official
W24Exceptions. This allows us to mock consistent responses
even when the files are rejected before they reach the API
"""

# Default Authentication Region
DEFAULT_AUTH_REGION = "eu-central-1"

# Default Endpoints
DEFAULT_SERVER_WSS = "ws-api.w24.co"
DEFAULT_SERVER_HTTPS = "support.w24.co"

# List of the Locations where we are looking for the license file
# if the user does not specify a path.
LICENSE_LOCATIONS = (".werk24", "werk24_license.txt")

LICENSE_ERROR_TEXT = """
--------------------------------------------------------------------------------

####   ####   #### ########### ##########    ####   #####     ##################
####  #####  ####  ####        ####   #####  ####  ####     #####   #####  #####
 #### ###### ####  ####        ####    ####  #########     ##### ##  ###   #####
 #### ###### ####  ##########  ###########   ########      ######## ### #  #####
  ###### #######   ####        ##########    ##########    ###### ####      ####
  ######  ######   ####        ####   ####   ####  #####   #####     ####  #####
   ####   #####    ########### ####    ####  ####   #####  ###################

--------------------------------------------------------------------------------

General Information
-------------------
Werk24 is a specialized commercial company dedicated to extracting information
from technical documents. The python client you are currently using is designed
to facilitate seamless interaction with our advanced server infrastructure.

License File
------------
We were unable to locate a license file, please schedule a first meeting with
us to learn about the possibilities of our technology:


        >>> https://werk24.io/schedule-a-call?w24cli_license_error <<<


Thank you.
--------------------------------------------------------------------------------
"""


class Hook(BaseModel):
    """
    A Utility class to register callback requests for a specific message_type or W24Ask.

    The 'Hook' object is used for handling and maintaining callback requests. Registering
    an 'ask' should include a complete W24Ask definition, not just the ask type.

    Attributes:
    ----------
    message_type (Optional[W24TechreadMessageType]): Specifies the type of the message.
    message_subtype (Optional[W24TechreadMessageSubtype]): Specifies the subtype of the message.
    ask (Optional[W24Ask]): The complete definition of W24Ask, if any.
    function (Callable): The callback function to be invoked when the resulting information
        is available.

    Note:
    ----
    Either a message_type or an ask must be registered. Be careful when registering an ask;
    a complete W24Ask definition is required, not just the ask type.
    """

    message_type: Optional[W24TechreadMessageType] = None
    message_subtype: Optional[W24TechreadMessageSubtype] = None
    ask: Optional[W24Ask] = None
    function: Callable


class W24TechreadClient:
    """Simple W24Client that allows you to use
    learn more about the content on your Technical
    Drawings.
    """

    def __init__(
        self,
        techread_server_wss: str,
        techread_version: str,
        development_key: str = None,
        support_base_url: str = DEFAULT_SERVER_HTTPS,
        wss_close_timeout: int = 600,
    ):
        """
        Initialize a new W24TechreadClient.

        If you wonder about any of the attributes, have a
        look at the .env file that we provided to you.
        They contain all the information that you will need.

        Args:
        ----
        - techread_server_wss (str): domain name that
            is being used by the websocket client
        - techread_version (str): version that you want to
            connect to
        - development_key (str): key that allows you to submit
            your request to one of the internal architectures.
            You can try guessing or bruteforcing this key;
            we'll just charge you for every request you submit and
            transfer the money to the holiday bonus account.
        """
        self._development_key = development_key

        # Create an empty reference to the authentication
        # service necessary for the Cognito Authentication.
        self._auth_client: Optional[AuthClient] = None

        # HTTP Client
        self._techread_client_https = TechreadClientHttps(
            techread_version,
            support_base_url,
        )

        # WSS Client
        self._techread_client_wss = TechreadClientWss(
            techread_server_wss, techread_version, wss_close_timeout
        )

    async def __aenter__(self) -> "W24TechreadClient":
        """Create the HTTPS and WSS sessions

        Raises:
        ------
        - RuntimeError: Exception is raised if you tried to enter 
            a session before calling the register() method

        Returns:
        -------
        - W24TechreadClient: Version of self with active sessions
        """
        logging.debug("Entering the session")
        await asyncio.gather(
            self._techread_client_https.__aenter__(),
            self._techread_client_wss.__aenter__()
        )
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        """
        Ensure that the sessions are closed
        """
        logging.debug("Exiting the session")
        await asyncio.gather(
            self._techread_client_https.__aexit__(exc_type, exc_value, traceback),
            self._techread_client_wss.__aexit__(exc_type, exc_value, traceback)
        )

    def register(
        self,
        cognito_region: Optional[str] = None,
        cognito_identity_pool_id: Optional[str] = None,
        cognito_user_pool_id: Optional[str] = None,
        cognito_client_id: Optional[str] = None,
        cognito_client_secret: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        token: Optional[str] = None,
    ) -> None:
        """
        Register with the authentication service (i.e., lazy login)

        Note:
        ----
        The Cognito Authentication is only present for backwards
        compatibility. We have moved to a token-based system.
        
        Args:
        ----
        - cognito_region (str): Physical region
        - cognito_identity_pool_id (str): identity pool of W24
        - cognito_client_id (str): the client id of your application
        - cognito_client_secret (str): the client secret of your
            application
        - username (str): the username with which you want to register
        - password (str): the password with which you want to register
        """
        # create an client instance to connect
        # to the authentication service
        self._auth_client = AuthClient(
            cognito_region,
            cognito_identity_pool_id,
            cognito_user_pool_id,
            cognito_client_id,
            cognito_client_secret,
            username,
            password,
            token,
        )
        # ensure that we have a token
        try:
            logging.debug("Authenticating with the authentication service")
            self._auth_client.login()  # type: ignore
        except AttributeError as exc:
            raise RuntimeError(
                "No connection to the authentication service was "
                + "established. Please call register()"
            ) from exc

        # tell the techread clients about it
        self._techread_client_https.register_auth_client(self._auth_client)
        self._techread_client_wss.register_auth_client(self._auth_client)

    @staticmethod
    def generate_encryption_keys(passphrase: bytes) -> Tuple[bytes, bytes]:
        """
        Generate a new RSA key pair and return the private and public key 
        as PEM encoded bytes.

        Args:
        ----
        - passphrase (bytes): The passphrase to encrypt the private key with.

        Returns:
        -------
        - Tuple[bytes, bytes]: The private key and public key as PEM encoded bytes.
        """
        logger.debug("Generating new RSA key pair")
        return generate_new_key_pair(passphrase=passphrase)

    @staticmethod
    def encrypt_with_public_key(public_key_pem: bytes, data: bytes) -> bytes:
        """
        Encrypt the data with the given public key.

        Args:
        ----
        - public_key_pem (bytes): The public key to use for encryption.
        - data (bytes): The data to encrypt.

        Returns:
        -------
        bytes: The encrypted data.
        """
        logger.debug("Encrypting data with public key")
        return encrypt_with_public_key(public_key_pem, data)

    @staticmethod
    def decrypt_with_private_key(
        private_key_pem: bytes, password: bytes, data: bytes
    ) -> bytes:
        """
        Decrypt the data with the given private key.

        Args:
        ----
        private_key_pem (bytes): The private key to use for decryption.
        data (bytes): The data to decrypt.

        Returns:
        -------
        bytes: The decrypted data.
        """
        logger.debug("Decrypting data with private key")
        return decrypt_with_private_key(private_key_pem, password, data)

    async def read_drawing(
        self,
        drawing: Union[BufferedReader, bytes],
        asks: List[W24Ask],
        model: bytes = None,
        max_pages: int = 1,
        drawing_filename: Optional[str] = None,
        sub_account: Optional[UUID4] = None,
        client_public_key_pem: Optional[bytes] = None,
        client_private_key_pem: Optional[bytes] = None,
        client_private_key_passphrase: Optional[bytes] = None,
    ) -> AsyncIterator[W24TechreadMessage]:
        """
        Send a Technical Drawing to the W24 API to read it.

        Args:
        ----
        - drawing (bytes): binary representation of a technical drawing.
            Please refer to the API - documentation to learn which mime
            types are supported.
        - model (bytes): binary representation of the 3d model (typically
            step). This is currently not being used and may come back
            later again.
        - asks (List[W24Ask]): List of Asks that are requested from the API.
            They must derive from the W24Ask object. Refer to the API
            documentation for a full list of supported W24AskTypes
        - max_pages (int): Maximum number of pages that are being processed
            of the submitted file. This protects platform users from
            costly requests caused by a user uploading a single file with
            many pages.
        - drawing_filename (str|None): Optional information about the
            filename of the drawing. Frequently this contains information
            about the drawing id and you can make that information
            available to us through this parameter. If you don't know the
            filename, don't worry, it will still work.
        - sub_account (UUID4|None): Optional specification of the sub-account
            that the request should be attributed to. Sub-accounts allow
            you to manage several customers at the same time and receiving
            separate positions on the monthly invoice.
        - client_public_key_pem (bytes|None): Public key that the server shall
            use to encrypt the callback request. This is only necessary if
            you want to receive the callback in an encrypted form. The
            availability of this feature may depend on your service level.
        - client_private_key_pem (bytes|None): Private key that the server shall
            use to encrypt the callback request. This is only necessary if
            you want to receive the callback in an encrypted form. The
            availability of this feature may depend on your service level.
        - client_private_key_passphrase (bytes|None): Passphrase to decrypt the
            private key. This is only necessary if you want to receive the
            callback in an encrypted form. The availability of this feature
            may depend on your service level.

        Yields:
        ------
        - W24TechreadMessage: Response object obtained from the API
            that indicates the state of your request. Be sure to pass this
            to the read_drawing_listen method

        Raises:
        ------
        - DrawingTooLarge: Exception is raised when the drawing was too
            large to be processed. At the time of writing. The upload
            limit lies at 6 MB (including overhead).
        - UnsupportedMediaType: Exception is raised when the drawing or
            model is submitted in any data type other than bytes.

        """
        # give us some debug information
        logger.debug("API method read_drawing() called")

        # quickly check whether the input type is bytes. If it is string,
        # the presigned-AWS post interestingly returns a 403 error_code
        # without additional information. We want to inform the caller
        # that they submitted the wrong data type.
        # See Github Issue #13
        if not isinstance(drawing, (BufferedReader, bytes)):
            logger.warning("Unsupported media type for drawing")
            raise UnsupportedMediaType(
                "Drawing bytes requires 'bytes' or 'BufferedReader' type"
            )

        # send the initiation command
        init_message, init_response = await self.init_request(
            asks, max_pages, drawing_filename, sub_account
        )
        logger.debug("Init request sent and response received.")

        yield init_message

        # stop if the response is unsuccessful.
        if not init_response.is_successful:
            logger.warning("Init request was not successful.")
            return

        # Start reading the file
        async for message in self.read_request(
            init_response,
            asks,
            drawing,
            model,
            client_public_key_pem,
            client_private_key_pem,
            client_private_key_passphrase,
        ):
            yield message

    async def read_request(
        self,
        init_response: W24TechreadInitResponse,
        asks: List[W24Ask],
        drawing: Union[bytes, BufferedReader],
        model: Optional[bytes] = None,
        client_public_key_pem: Optional[bytes] = None,
        client_private_key_pem: Optional[bytes] = None,
        client_private_key_passphrase: Optional[bytes] = None,
    ) -> AsyncGenerator[W24TechreadMessage, None]:
        """
        Read the request after obtaining the init_response.

        This is helpful when we want to perform the reading
        in the background or in a separate thread.

        Args:
        ----
        - init_response (W24TechreadInitResponse): InitResponse that
            was obtained from the init_request method
        - asks (List[W24Ask]): List of asks that we are asking for.
            This is only used for error handling here.
        - drawing (bytes): Drawing bytes that shall be uploaded
        - model (Optional[bytes], optional): Optional model bytes.
            Defaults to None.
        - client_public_key_pem (Optional[bytes], optional): Public
            key that the server shall use to encrypt the callback
            request. Defaults to None.
        - client_encryption_passphrase (Optional[bytes], optional):
            Passphrase to encrypt the private key. Defaults to None.

        Yields:
        ------
        - W24TechreadMessage: Messages that are received after the
            request was submitted
        """
        logger.debug("API method read_request() called")
        # If the server wants us to encrypt the file, we will do so
        if init_response.public_key is None:
            logger.info(
                "No public key was provided by the server. "
                "Consider upgrading to a higher service level if you need end2end encryption."
            )
            server_public_key = None
        else:
            logger.info("Public key was provided by the server")
            server_public_key = init_response.public_key.encode("utf-8")

        # upload drawing and model. We can do that in parallel.
        # If your user uploads them separately, you could also
        # upload them separately to Werk24.
        try:
            logger.debug("Uploading drawing")
            await self._techread_client_https.upload_associated_file(
                init_response.drawing_presigned_post,
                drawing,
                public_server_key=server_public_key,
            )
            logger.debug("Drawing uploaded")

        # explicitly reraise the exception if the payload is too large
        except (BadRequestException, RequestTooLargeException) as exception:
            async for message in self._trigger_asks_exception(asks, exception):
                yield message
            return

        # Tell Werk24 that all the files have been uploaded
        # correctly and the reading process can be started.
        #
        # NOTE: you will only be able to start the reading
        # process from the websocket connection that
        # initiated the request. If you want to run a
        # stateless-system that separates the initialization
        # from the upload and read stages, you'll need to
        # find a way of handing over the tcp connection :)
        # PS: The AWS API Gateway for websockets might help you
        # here.
        async for message in self._send_command_read(
            client_public_key_pem,
            client_private_key_pem,
            client_private_key_passphrase,
        ):
            yield message

    async def init_request(
        self,
        asks: List[W24Ask],
        max_pages: int,
        drawing_filename: Optional[str],
        sub_account: Optional[UUID4],
    ) -> Tuple[W24TechreadMessage, W24TechreadInitResponse]:
        """
        Initialize a new techread request.

        This method is useful if you want to separate the
        initialization from the upload and read stages.

        This achieves two things:
        1. The server has a couple of 100ms to
           reserves some resources for you, and
        2. The server will create a new request_id
           that you will need when uploading the
           associated files

        Args:
        ----
        - asks (List[W24Ask]): Asks for this request.
        - max_pages (int): Maximum pages to be read.
        - drawing_filename (Optional[str]): Filename of the drawing, if any.
        - sub_account (Optional[UUID4]): Sub-account ID, if any.

        Returns:
        -------
        - Tuple[W24TechreadMessage, W24TechreadInitResponse]: Received
            message and init response.
        """
        logger.debug("API method init_request() called")
        request = W24TechreadRequest(
            asks=asks,
            development_key=self._development_key,
            max_pages=max_pages,
            drawing_filename=drawing_filename,
            sub_account=sub_account,
        )

        await self._techread_client_wss.send_command(
            W24TechreadAction.INITIALIZE.value,
            request.model_dump_json(),
        )
        logger.debug("Techread request submitted")

        message = await self._techread_client_wss.recv_message()
        logger.info("Received request_id %s", message.request_id)

        try:
            response = W24TechreadInitResponse.model_validate(message.payload_dict)
        except ValueError as exception:
            error_message = message.payload_dict.get("message")
            if error_message is not None:
                raise ServerException(error_message) from exception

        return message, response

    async def _send_command_read(
        self,
        client_public_key_pem: Optional[bytes] = None,
        client_private_key_pem: Optional[bytes] = None,
        client_private_key_passphrase: Optional[bytes] = None,
    ) -> AsyncGenerator[W24TechreadMessage, None]:
        """
        Send the request request to the backend
        and yield the resulting messages.

        Yields:
        ------
        - W24TechreadMessage: Receiving messages
        """
        logger.debug("API method _send_command_read() called")
        if client_public_key_pem is not None:
            message = {"public_key": client_public_key_pem.decode("utf-8")}
        else:
            message = {}

        # submit the request the to the API
        logger.debug("Sending techread request")
        await self._techread_client_wss.send_command(
            W24TechreadAction.READ.value, 
            json.dumps(message),
        )
        logger.debug("Techread request submitted")

        # Wait for incoming messages from the server.
        # They will tell you when the individual
        # asks become available. The socket returns
        # strings of jsonified W24TechreadMessage objects.
        #
        # The loop will stop when the websocket is closed
        async for message in self._techread_client_wss.listen():
            logger.debug("Received message %s:%s", message.message_type, message.message_subtype)
            if message.payload_url is not None:
                message.payload_bytes = (
                    await self._techread_client_https.download_payload(
                        message.payload_url,
                        client_private_key_pem,
                        client_private_key_passphrase,
                    )
                )

            # return the message to the caller for immediate
            # consumption
            yield message
    

    @staticmethod
    async def _trigger_asks_exception(
        asks: List[W24Ask],
        exception_raw: Union[BadRequestException, RequestTooLargeException],
    ) -> AsyncGenerator[W24TechreadMessage, None]:
        """
        Trigger exceptions for all the submitted asks.

        This helps us to mock consistent exception handling
        behavior even when the files are rejected before they
        reach the API.

        Args:
        ----
        - asks (List[W24Ask]): List of all submitted asks
        - exception (RequestTooLargeException): Exception
            that shall be pushed

        Yields:
        ------
        - W24TechreadMessage: Exception message
        """
        logger.debug("API method _trigger_asks_exception() called")

        # get the exception type from the MAP
        try:
            exception_type = EXCEPTION_MAP[type(exception_raw)]

        # if we see an exception that we were not supposed
        # to handle, there must have been a developer passing
        # a new exception type. Let's tell her by rasing
        # a runtime error
        except KeyError as exception:
            raise RuntimeError(
                "Unknown exception type passed: %s" % type(exception_raw)
            ) from exception

        # translate the exception into an official exception
        exception = W24TechreadException(
            exception_level=W24TechreadExceptionLevel.ERROR,
            exception_type=exception_type,
        )

        # then yield one message for each of the requested asks
        for cur_ask in asks:
            yield W24TechreadMessage(
                request_id=uuid.uuid4(),
                message_type=W24TechreadMessageType.ASK,
                message_subtype=cur_ask.ask_type,
                exceptions=[exception],
            )

    @classmethod
    def _get_license_environs(cls, license_path: Optional[str]) -> Dict[str, str]:
        """Get the environment variables
        Where we either select the variables from the license
        files. If that fails we fall back to the true environment
        variables.

        NOTE: We do not want to mix the sources.

        Args:
        ----
        - license_path (Optional[str]): Path of the license files

        Returns:
        -------
        - Dict[str,str]: Key, Value pairs for the environment variables

        Raises:
        ------
        - LicenseError: If the defined license path doesn't exist or if
            relevant environment variable isn't found
        """
        logger.debug("API method _get_license_environs() called")

        # Mimick the old default value of .werk24
        if license_path is None:
            license_path = next(filter(os.path.exists, LICENSE_LOCATIONS), None)
            logger.debug("License path set to %s", license_path)

        # First priority: look for the local license path
        if license_path is not None and os.path.exists(license_path):
            environs_raw = {
                k: v for k, v in dotenv.dotenv_values(license_path).items() if v
            }
        
        # if the caller defined a license path, but it does not exist, raise the exception
        elif license_path is not None:
            logger.warn("License path specified but not valid: %s", license_path)
            raise LicenseError(LICENSE_ERROR_TEXT)

        # Second priority: use the environment variables
        else:
            environs_raw = dict(os.environ)

        return environs_raw

    @classmethod
    def make_from_token(
        cls,
        token: str,
        region: Optional[str] = None,
        server_https: Optional[str] = None,
        server_wss: Optional[str] = None,
        version: str = "v2",
        wss_close_timeout: int = 600,
    ) -> "W24TechreadClient":
        logger.debug("API method make_from_token() called")

        # create a reference to the client
        server_https = server_https or DEFAULT_SERVER_HTTPS
        server_wss = server_wss or DEFAULT_SERVER_WSS
        client = W24TechreadClient(server_wss, version, wss_close_timeout=wss_close_timeout)

        # register the credentials. This will in effect
        # only set the variabels in the authorizer. It will
        # not trigger a network request
        client.register(cognito_region=region, token=token)

        # return the client
        return client

    @classmethod
    def make_from_env(
        cls,
        license_path: Optional[str] = None,
        auth_region: Optional[str] = None,
        server_https: Optional[str] = None,
        server_wss: Optional[str] = None,
        version: str = "v2",
        wss_close_timeout: int = 600,
    ) -> "W24TechreadClient":
        """
        Small helper function that creates a new
        W24TechreadClient from the environment info.

        Args:
        ----
        - license_path (Optional[str]: path to the License file.
            By default we are looking for a .werk24 or werk24_license.txt
            file in the current cwd. If argument is set to None, we are
            not loading any file and relying on the ENVIRONMENT variables only
        - auth_region (Optional[str]): AWS Region of the Authentication
            Service.
            Takes priority over environ W24TECHREAD_AUTH_REGION and
            DEFAULT_AUTH_REGION
        - server_https (Optional[str]): HTTPS endpoint of the Werk24 API.
            Takes priority over environ W24TECHREAD_SERVER_HTTPS and
            DEFAULT_SEVER_HTTPS
        - version (Optional[str]): Version of the Werk24 API.
            Takes priority over environ W24TECHREAD_VERSION and
            DEfAULT_VERSION
        - wss_close_timeout (int): Timeout for the WSS connection.
            Defaults to 600 seconds.

        Raises:
        ------
        - FileNotFoundError: Raised when you pass a path to a license file
            that does not exist
        - UnauthorizedException: Raised when the credentials were not
            accepted by the API

        Returns:
        -------
        - W24TechreadClient: The techread Client
        """
        logger.debug("API method make_from_env() called")

        # get the license variables from the environment variables and
        # the license file.
        environs = cls._get_license_environs(license_path)

        # define a small helper function that finds the first valid
        # value in the supplied list of possible values
        def pick_env(var: Optional[str], env_key: str, default: str) -> str:
            return var or environs.get(env_key, default)

        # then make sure we use the correct priorities
        auth_region = pick_env(
            auth_region, "W24TECHREAD_AUTH_REGION", DEFAULT_AUTH_REGION
        )
        logger.debug("Auth region set to %s", auth_region)

        server_wss = pick_env(
            server_wss, "W24TECHREAD_SERVER_WSS_V2", DEFAULT_SERVER_WSS
        )
        logger.debug("Server WSS set to %s", server_wss)

        # get the variables from the environment and ensure that they
        # are set. If not, raise an exception
        try:
            # create a reference to the client
            client = W24TechreadClient(server_wss, version, wss_close_timeout=wss_close_timeout)

            # register the credentials. This will in effect
            # only set the variabels in the authorizer. It will
            # not trigger a network request
            client.register(
                auth_region,
                environs.get("W24TECHREAD_AUTH_IDENTITY_POOL_ID"),
                environs.get("W24TECHREAD_AUTH_USER_POOL_ID"),
                environs.get("W24TECHREAD_AUTH_CLIENT_ID"),
                environs.get("W24TECHREAD_AUTH_CLIENT_SECRET"),
                environs.get("W24TECHREAD_AUTH_USERNAME"),
                environs.get("W24TECHREAD_AUTH_PASSWORD"),
                environs.get("W24TECHREAD_AUTH_TOKEN"),
            )

        except KeyError:
            raise LicenseError(LICENSE_ERROR_TEXT)

        # return the client
        return client

    async def read_drawing_with_callback(
        self,
        drawing: Union[BufferedReader, bytes],
        asks: List[W24Ask],
        callback_url: str,
        max_pages: int = 5,
        drawing_filename: Optional[str] = None,
        callback_headers: Optional[Dict[str, str]] = None,
        public_key: Optional[bytes] = None,
    ) -> UUID4:
        """
        Read the Drawings and register a callback URL.

        This method is useful if you want to separate the initialization from the 
        upload and read stages.

        You can simply specify the callback URL that shall receive the message responses. 
        This function will return after sending the request to the API. The callback URL 
        will be called asynchronously. Keep in mind that the callback speed depends on your
        service level.

        Args:
        ----
        - drawing (Union[BufferedReader, bytes]):
            Drawing that you want to process
        - asks (List[W24Ask]):
            List of all the information that you want to obtain
        - callback_url (str):
            URL that shall receive the callback requests
        - max_pages (int, optional):
            Maximum number of pages that shall be processed.
            Defaults to 5.
        - drawing_filename (Optional[str], optional):
            Filename of the drawing. Defaults to None.
        - callback_headers (Optional[Dict[str, str]], optional):
            Headers that shall be sent with the callback request. Defaults to None.
        - public_key (Optional[bytes], optional):
            Public key that the server shall use to encrypt the callback request. Defaults to None.
            Note: availability of this feature may depend on your service level.

        Raises:
        ------
        - ServerException: Raised when the server returns an ERROR message
        - InsufficentCreditsException: Raised when the user does not have enough credits 
            to perform the request

        Returns:
        -------
        - UUID4: Request ID of the request
        """
        logger.debug("API method read_drawing_with_callback() called")

        # send the request to the API
        try:
            return await self._techread_client_https.read_drawing_with_callback(
                drawing,
                asks,
                callback_url,
                max_pages=max_pages,
                drawing_filename=drawing_filename,
                callback_headers=callback_headers,
                public_key=public_key,
            )
        except ServerException:
            raise
        except InsufficientCreditsException:
            raise

    async def read_drawing_with_hooks(
        self,
        drawing: Union[BufferedReader, bytes],
        hooks: List[Hook],
        max_pages: int = 5,
        drawing_filename: Optional[str] = None,
        sub_account: Optional[UUID4] = None,
        client_public_key_pem: Optional[bytes] = None,
        client_private_key_pem: Optional[bytes] = None,
        client_private_key_passphrase: Optional[bytes] = None,
    ) -> None:
        """
        Send the drawing to the API (can be PDF or image)
        and register a number of callbacks that are triggered
        once the asks become available.

        Args:
        ----
        - drawing_bytes (bytes): Technical Drawing as Image or PDF
        - hooks (List[Hook]): List of Callback you want to obtain

        Raises:
        ------
        - ServerException: Raised when the server returns an ERROR message
        """
        logger.debug("API method read_drawing_with_hooks() called")

        # filter the callback requests to only contain
        # the ask types
        asks_list = [cur_ask.ask for cur_ask in hooks if cur_ask.ask is not None]
        logger.debug("Filtered asks: %s", asks_list)

        try:
            # send out the request and make a generator
            # that triggers when the result of an ask
            # becomes available
            async for message in self.read_drawing(
                drawing,
                asks_list,
                max_pages=max_pages,
                drawing_filename=drawing_filename,
                sub_account=sub_account,
                client_public_key_pem=client_public_key_pem,
                client_private_key_pem=client_private_key_pem,
                client_private_key_passphrase=client_private_key_passphrase,
            ):
                await self.call_hooks_for_message(message, hooks)

        # explicitly reraise server exceptions
        except ServerException:  # pylint: disable=try-except-raise
            raise

    async def call_hooks_for_message(
        self, message: W24TechreadMessage, hooks: List[Hook]
    ) -> None:
        """
        Call the hook function for the response message.

        Args:
        ----
        - message (W24TechreadMessage): Message returned from the
            read_drawing method
        - hooks (List[Hook]): List of hooks from which we need to
            pick the suited one

        Raises:
        ------
        - ServerException: raised when the server returns an ERROR
            message
        """
        logger.debug("API method call_hooks_for_message() called")
        hook_function = self._get_hook_function_for_message(message, hooks)
        if hook_function is None:
            return

        # if the hook_function is not callable, we want to warn the user,
        # rather than throwing an exception
        if not callable(hook_function):
            logger.warning(
                "You registered a non-callable trigger of type '%s' with "
                "the message_type '%s'. Please make sure that you are using "
                "a Callable (e.g, def or lambda)",
                type(hook_function),
                message.message_type,
            )
            return

        # if everything went well, we call the trigger with
        # the message as payload. Be sure to call the
        # function asymmetrically if supported
        (
            await hook_function(message)
            if iscoroutinefunction(hook_function)
            else hook_function(message)
        )

    @staticmethod
    def _get_hook_function_for_message(
        message: W24TechreadMessage, hooks: List[Hook]
    ) -> Optional[Callable]:
        """
        Get the hook function that corresponds to the message type.

        Args:
        ----
        - message (W24TechreadMessage): Message returned from the read_drawing method
        - hooks (List[Hook]): List of hooks from which we need to pick the suited one

        Returns:
        -------
        - Optional[Callable]: Hook function that should be called
        """
        logger.debug("API method _get_hook_function_for_message() called")

        def hook_filter(hook: Hook) -> bool:
            if message.message_type == W24TechreadMessageType.ASK:
                return (
                    hook.ask is not None
                    and message.message_subtype.value == hook.ask.ask_type.value
                )
            else:
                return (
                    hook.message_type is not None
                    and hook.message_subtype is not None
                    and message.message_type == hook.message_type
                    and message.message_subtype == hook.message_subtype
                )

        # return the first positive case
        for cur_hook in filter(hook_filter, hooks):
            return cur_hook.function

        # if we are still here, we have an unknown message type, which
        # probably is being caused by an API update. We want to ensure
        # that the user is being informed, but we do not want to break
        # the existing functionality -> warning
        logger.debug(
            "Ignoring message of type %s:%s - no hook registered",  # noqa
            message.message_type,
            message.message_subtype,
        )
        return None

    async def create_helpdesk_task(self, task: W24HelpdeskTask) -> W24HelpdeskTask:
        """
        Create a Helpdesk ticket.

        Args:
        ----
        - task (W24HelpdeskTask): Helpdesk task to be created

        Raises:
        ------
        - BadRequestException: Raised when the request body
            cannot be interpreted. This normally indicates
            that the API version has been updated and that
            we missed a corner case. If you encounter this
            exception, it is very likely our mistake. Please
            get in touch!
        - UnauthorizedException: Raised when the token
            or the requested file have expired
        - ResourceNotFoundException: Raised when you are requesting
            an endpoint that does not exist. Again, you should
            not encounter this, but if you do, let us know.
        - RequestTooLargeException: Raised when the status
            code was 413
        - UnsupportedMediaTypException: Raised when the file you
            submitted cannot be read(because its media type
            is not supported by the API).
        - ServerException: Raised for all other status codes
            that are not 2xx

        Returns:
        -------
        - W24HelpdeskTask: Created helpdesk task with an updated task_id.
        """
        logger.debug("API method create_helpdesk_task() called")
        return await self._techread_client_https.create_helpdesk_task(task)
