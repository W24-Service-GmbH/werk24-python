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
                callback=lambda msg: print("Received Thumbnail of Page")
        ]))
"""
import logging
import os
import uuid
from asyncio import gather, iscoroutinefunction
from types import TracebackType
from typing import (AsyncGenerator, AsyncIterator, Callable, Dict, List,
                    Optional, Type)

import dotenv
from pydantic import BaseModel

from werk24.auth_client import AuthClient
from werk24.exceptions import (BadRequestException, LicenseError,
                               RequestTooLargeException, ServerException,
                               UnsupportedMediaType)
from werk24.models.ask import W24Ask
from werk24.models.techread import (W24TechreadAction, W24TechreadException,
                                    W24TechreadExceptionLevel,
                                    W24TechreadExceptionType,
                                    W24TechreadInitResponse,
                                    W24TechreadMessage,
                                    W24TechreadMessageSubtype,
                                    W24TechreadMessageType, W24TechreadRequest)
from werk24.techread_client_https import TechreadClientHttps
from werk24.techread_client_wss import TechreadClientWss

# make the logger
logger = logging.getLogger(  # pylint: disable=invalid-name
    'w24_techread_client')

ENVIRONS = [
    "W24TECHREAD_SERVER_HTTPS",
    "W24TECHREAD_SERVER_WSS",
    "W24TECHREAD_VERSION",
    "W24TECHREAD_AUTH_CLIENT_ID",
    "W24TECHREAD_AUTH_CLIENT_SECRET",
    "W24TECHREAD_AUTH_IDENTITY_POOL_ID",
    "W24TECHREAD_AUTH_USER_POOL_ID",
    "W24TECHREAD_AUTH_USERNAME",
    "W24TECHREAD_AUTH_PASSWORD",
    "W24TECHREAD_AUTH_REGION"
]
""" List of the environment variables used by the
client """


EXCEPTION_MAP = {
    RequestTooLargeException:
        W24TechreadExceptionType.DRAWING_FILE_SIZE_TOO_LARGE,
    BadRequestException:
        W24TechreadExceptionType.DRAWING_FILE_SIZE_TOO_LARGE
}
""" Map to translate the local exceptions to offical
W24Exceptions. This allows us to mock consistent responses
even when the files are rejected before they reach the API
"""

DEFAULT_AUTH_REGION = "eu-central-1"
DEFAULT_SERVER_HTTPS = "techread.w24.io"
DEFAULT_SERVER_WSS = "techread-ws.w24.io"
DEFAULT_VERSION = "v1"


class Hook(BaseModel):
    """ Small Object to keep the callback requests.
    You can either register a callback request to an
    ask or a message_type.

    If you register an ask, be sure to use a complete W24Ask
    definition; not just the ask type.
    """
    message_type: Optional[W24TechreadMessageType]
    message_subtype: Optional[W24TechreadMessageSubtype]
    ask: Optional[W24Ask]
    function: Callable


class W24TechreadClient:
    """ Simple W24Client that allows you to use
    learn more about the content on your Technical
    Drawings.
    """

    def __init__(
        self,
        techread_server_https: str,
        techread_server_wss: str,
        techread_version: str,
        development_key: str = None
    ):
        """ Initialize a new W24TechreadClient. If you wonder
        about any of the attributes, have a look at the .env
        file that we provided to you. They contain all the
        information that you will need.

        Arguments:
            techread_server_https {str} -- domain name that
                is being used by the https client

            techread_server_wss {str} -- domain name that
                is being used by the websocket client

            techread_version {str} -- version that you want to
                connect to

            development_key {str} -- key that allows you to submit
                your request to one of the internal architectures.
                You can try guessing or bruteforcing this key;
                we'll just charge you for every request you submit and
                transfer the money to the holiday bonus account.
        """

        # save the development_key
        self._development_key = development_key

        # Create an empty reference to the authentication
        # service (currently AWS Cognito)
        self._auth_client: Optional[AuthClient] = None

        # Initialize an instance of the HTTPS client
        self._techread_client_https = TechreadClientHttps(
            techread_server_https, techread_version)

        # Initialize an instance of the WEBSCOKET client
        self._techread_client_wss = TechreadClientWss(
            techread_server_wss, techread_version)

    async def __aenter__(
            self
    ) -> 'W24TechreadClient':
        """ Create the HTTPS and WSS sessions

        Raises:
            RuntimeError: Exception is raised if
                you tried to enter a session before
                calling the register() method

        Returns:
            W24TechreadClient -- Version of self with
                active sessions
        """

        # enter the https session
        await self._techread_client_https.__aenter__()

        # enter the wss session
        await self._techread_client_wss.__aenter__()

        # return the "entered" version of self
        return self

    async def __aexit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc_value: Optional[BaseException],
            traceback: Optional[TracebackType]
    ) -> None:

        """ Ensure that the sessions are closed
        """

        # close the HTTPS session
        await self._techread_client_https.__aexit__(
            exc_type, exc_value, traceback)

        # close the WSS session
        await self._techread_client_wss.__aexit__(
            exc_type, exc_value, traceback)

    def register(
        self,
        cognito_region: str,
        cognito_identity_pool_id: str,
        cognito_user_pool_id: str,
        cognito_client_id: str,
        cognito_client_secret: str,
        username: str,
        password: str
    ) -> None:
        """
        Register with the authentication
        service (i.e., lazy login)

        Arguments:
            cognito_region {str} -- Physical region
            cognito_identity_pool_id {str} -- identity pool of W24
            cognito_client_id {str} -- the client id of your application
            cognito_client_secret {str} -- the client secrect of your
                application
            username {str} -- the username with which you want to register
            password {str} -- the password with which you want to register
        """
        # create an client instance to connect
        # to the authentication service
        self._auth_client = AuthClient(
            cognito_region,
            cognito_identity_pool_id,
            cognito_user_pool_id,
            cognito_client_id,
            cognito_client_secret)

        # register username and password
        self._auth_client.register(username, password)

        # tell the techread clients about it
        self._techread_client_https.register_auth_client(self._auth_client)
        self._techread_client_wss.register_auth_client(self._auth_client)

        # ensure that we have a token
        try:
            self._auth_client.login()  # type: ignore
        except AttributeError:
            raise RuntimeError(
                "No connection to the authentication service was " +
                "established. Please call register()")

    @property
    def username(self) -> Optional[str]:
        """ Make the username accessable to the CLI and GUI

        Returns:
            str: username of the currently registered user
        """
        try:
            return self._auth_client.username
        except ValueError:
            return None

    async def read_drawing(
        self,
        drawing: bytes,
        asks: List[W24Ask],
        model: bytes = None
    ) -> AsyncIterator[W24TechreadMessage]:
        """ Send a Technical Drawing to the W24 API to have it automatically
        interpreted and read. The API will return

        Arguments:
            drawing {bytes} -- binary representation of a technical drawing.
                Please refer to the API - documentation to learn which mime
                types are currently supported

        Keyword Arguments:
            model {bytes} -- binary represetation of the 3d model (typically
                step)
                Please refer to the API - documentation to learn whcih mime
                types are currently sypported(default: {None})

            asks {List[W24Ask]} --
                List of Asks that are requested from the API. They must derive
                from the W24Ask object. Refer to the API documentation for
                a full list of supported W24AskTypes

        Yields:
            W24TechreadMessage -- Response object obtained from the API
                that indicates the state of your request. Be sure to pass this
                to the read_drawing_listen method

        Raises:
            DrawingTooLarge -- Exception is raised when the drawing was too
                large to be processed. At the time of writing. The upload
                limit lies at 6 MB (including overhead).

            UnsupportedMediaType -- Exception is raised when the drawing or
                model is submitted in any data type other than bytes.
        """

        # quickly check whether the input type is bytes. If it is string,
        # the presigned-AWS post interestingly returns a 403 error_code
        # without additional information. We want to inform the caller
        # that they submitted the wrong data type.
        # See Github Issue #13
        if not isinstance(drawing, bytes):
            raise UnsupportedMediaType("Drawing bytes requires 'bytes' type")

        # the same is true for the model bytes
        if model is not None and not isinstance(model, bytes):
            raise UnsupportedMediaType("Model bytes requires 'bytes' type")

        # give us some debug information
        logger.info("API method read_drawing() called")

        # tell us when a development key is being used
        if self._development_key:  # pragma: no cover
            logger.info("Using development key %s***",
                        self._development_key[:8])

        # send the initiation command
        init_response = await self._send_command_init(asks)

        # upload drawing and model. We can do that in parallel.
        # If your user uploads them separately, you could also
        # upload them separately to Werk24.
        try:
            await gather(
                self._techread_client_https.upload_associated_file(
                    init_response.drawing_presigned_post,
                    drawing),
                self._techread_client_https.upload_associated_file(
                    init_response.model_presigned_post,
                    model))

        # explicitly reraise the exception if the payload is too
        # large
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
        # PS: The AWS API Gatway for websockets might help you
        # here.
        async for message in self._send_command_read():
            yield message

    async def _send_command_init(
        self,
        asks: List[W24Ask]
    ) -> W24TechreadInitResponse:
        """ Send the initiation command to the backend
        and return the associated response

        This achieves two things:
        1. The server has a couple of 100ms to
           reserves some resources for you, and
        2. The server will create a new request_id
           that you will need when uploading the
           associated files

        Args:
            asks (List[W24Ask]): List of asks that
                we are asking for in this request
        """
        request = W24TechreadRequest(
            asks=asks,
            development_key=self._development_key)

        await self._techread_client_wss.send_command(
            W24TechreadAction.INITIALIZE.value,
            request.json())

        response = await self._techread_client_wss.recv_message()
        logger.info("Received request_id %s", response.request_id)
        return W24TechreadInitResponse.parse_obj(response.payload_dict)

    async def _send_command_read(
        self
    ) -> AsyncGenerator[W24TechreadMessage, None]:
        """ Send the request request to the backend
        and yield the resulting messages

        Yields:
            W24TechreadMessage: Receiving messages
        """
        import time
        start = time.time()

        # submit the request the to the API
        await self._techread_client_wss.send_command(
            W24TechreadAction.READ.value,
            "{}")
        logger.info("Techread request submitted")

        # Wait for incoming messages from the server.
        # They will tell you when the individual
        # asks become available. The socket returns
        # strings of jsonified W24TechreadMessage objects.
        #
        # The loop will stop when the websocket is
        # closed
        async for message in self._techread_client_wss.listen():

            # check whether we need to download something
            if message.payload_url is not None:
                message.payload_bytes = await self._techread_client_https \
                    .download_payload(message.payload_url)
                start = time.time()

            # return the message to the caller for immediate
            # consumption
            yield message

    @staticmethod
    async def _trigger_asks_exception(
        asks: List[W24Ask],
        exception: RequestTooLargeException
    ) -> None:
        """ Trigger exceptions for all the submitted asks.
        This helps us to mock consistent exception handling
        behavior even when the files are rejected before they
        reach the API.

        Args:
            asks (List[W24Ask]): List of all submited asks
            exception (RequestTooLargeException): Exception
                that shall be pushed

        Yields:
            W24TechreadMessage: Exception message
        """

        # get the exception type from the MAP
        try:
            exception_type = EXCEPTION_MAP[type(exception)]

        # if we see an exception that we were not supposed
        # to handle, there must have been a developer passing
        # a new exception type. Let's tell her by rasing
        # a runtime error
        except KeyError:
            raise RuntimeError(
                f"Unknown exception type passed: {type(exception)}")

        # translate the exception into an official exception
        exception = W24TechreadException(
            exception_level=W24TechreadExceptionLevel.ERROR,
            exception_type=exception_type)

        # then yield one message for each of the requested asks
        for cur_ask in asks:
            yield W24TechreadMessage(
                request_id=uuid.uuid4(),
                message_type=W24TechreadMessageType.ASK,
                message_subtype=cur_ask.ask_type,
                exceptions=[exception])

    @ staticmethod
    def _get_license_environs(
        license_path: Optional[str]
    ) -> Dict[str, str]:
        """ Get the environment variables
        Where we either select the variables from the license
        files. If that fails we fall back to the true environment
        variables.

        NOTE: We do not want to mix the sources.

        Args:
            license_path (Optional[str]): Path of the license files

        Returns:
            Dict[str,str]: Key, Value pairs for the environment variables
        """

        # Mimick the old default value of .werk24
        if license_path is None and os.path.exists(".werk24"):
            license_path = ".werk24"  # pragma: no cover

        # First priority: look for the local license path
        if license_path is not None:
            if os.path.exists(license_path):
                environs_raw = {
                    k: v
                    for k, v in dotenv.dotenv_values(license_path).items()
                    if v is not None}

            # if the caller defined a license path, but it does not
            # exist, raise the exception
            else:
                raise LicenseError("Licence File not found")

        # Second priority: use the environment variables
        else:
            environs_raw = dict(os.environ)

        # filter the environment variables to only include the
        # ones that are relevant to us and return
        return {cur_key: environs_raw[cur_key] for cur_key in ENVIRONS}

    @classmethod
    def make_from_env(
        cls,
        license_path: Optional[str] = None,
        auth_region: Optional[str] = None,
        server_https: Optional[str] = None,
        server_wss: Optional[str] = None,
        version: Optional[str] = None
    ) -> "W24TechreadClient":
        """ Small helper function that creates a new
        W24TechreadClient from the enviorment info.

        Arguments:
            license_path:{Optional[str]} -- path to the License file.
                By default we are looking for a .werk24 file in the current
                cwd. If argument is set to None, we are not loading any
                file and relying on the ENVIRONMENT variables only

            auth_region: {Optional[str]} -- AWS Region of the Authentication
                Service.
                Takes priority over environ W24TECHREAD_AUTH_REGION and
                DEFAULT_AUTH_REGION

            server_https: {Optional[str]} -- HTTPS endpoint of the Werk24 API.
                Takes priority over environ W24TECHREAD_SERVER_HTTPS and
                DEFAULT_SEVER_HTTPS

            version: {Optional[str]} -- Version of the Werk24 API.
                Takes priority over environ W24TECHREAD_VERSION and
                DEfAULT_VERSION

        Raises:
            FileNotFoundError -- Raised when you pass a path to a license file
                that does not exist
            UnauthorizedException -- Raised when the credentials were not
                accepted by the API

        Returns:
            W24TechreadClient -- The techread Client
        """

        # get the licence variablles from the environment variables and
        # the license file.
        environs = cls._get_license_environs(license_path)

        # define a small helper function that finds the frist valid
        # value in the supplied list of possible values
        def pick_env(var: str, env_key: str, default: str) -> str:
            return var or environs.get(env_key) or default

        # then make sure we use the correct prioties
        auth_region = pick_env(
            auth_region, 'W24TECHREAD_AUTH_REGION', DEFAULT_AUTH_REGION)
        server_https = pick_env(
            server_https, 'W24TECHREAD_SERVER_HTTPS', DEFAULT_SERVER_HTTPS)
        server_wss = pick_env(
            server_wss, 'W24TECHREAD_SERVER_WSS', DEFAULT_SERVER_WSS)
        version = pick_env(version, 'W24TECHREAD_VERSION', DEFAULT_VERSION)

        # get the variables from the environment and ensure that they
        # are set. If not, raise an exception
        try:

            # create a reference to the client
            client = W24TechreadClient(server_https, server_wss, version)

            # register the credentials. This will in effect
            # only set the variabels in the authorizer. It will
            # not trigger a network request
            client.register(
                auth_region,
                environs['W24TECHREAD_AUTH_IDENTITY_POOL_ID'],
                environs['W24TECHREAD_AUTH_USER_POOL_ID'],
                environs['W24TECHREAD_AUTH_CLIENT_ID'],
                environs['W24TECHREAD_AUTH_CLIENT_SECRET'],
                environs['W24TECHREAD_AUTH_USERNAME'],
                environs['W24TECHREAD_AUTH_PASSWORD'])

        except KeyError:
            raise LicenseError(
                "The License information could neither be "
                "found in the local environment variables, nor in the "
                "local '.werk24' file. Please make sure that you are "
                "calling the client from the directory that contains "
                "your '.werk24' file and that the license file "
                "name does not contain a prefix.")

        # return the client
        return client

    async def read_drawing_with_hooks(
        self,
        drawing_bytes: bytes,
        hooks: List[Hook]
    ) -> None:
        """ Send the drawing to the API (can be PDF or image)
        and register a number of callbacks that are triggered
        once the asks become available.

        Arguments:
            drawing_bytes {bytes} -- Technical Drawing as Image or PDF
            hooks {List[Hook]} -- List of Callback you want to obtain

        Raises:
            ServerException -- Raised when the server returns an ERROR
                message
        """

        # filter the callback requests to only contain
        # the ask types
        asks_list = [
            cur_ask.ask
            for cur_ask in hooks
            if cur_ask.ask is not None]

        try:
            # send out the request and make a generator
            # that triggers when the result of an ask
            # becomes available
            async for message in self.read_drawing(drawing_bytes, asks_list):
                await self._call_hooks_for_message(message, hooks)

        # explicitly reraise server exceptions
        except ServerException:  # pylint: disable=try-except-raise
            raise

    async def _call_hooks_for_message(
            self,
            message: W24TechreadMessage,
            hooks: List[Hook]
    ) -> None:
        """ Find the correct hook for the read reseponse and
        call the corresponding hook.

        Arguments:
            message {W24TechreadMessage} -- Messsage returned from the
                read_drawing method

            hooks {List[Hook]} -- List of hooks from which we need to
                pick the suited one

        Raises:
            ServerException: raised when the server returns an ERROR
                message
        """

        # get the hook function that corresponds to the message
        hook_function = self._get_hook_function_for_message(message, hooks)

        # if no hook is registered, ignore
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
                message.message_type)
            return

        # if everything went well, we call the trigger with
        # the message as payload. Be sure to call the
        # function asymmetrically if supported
        if iscoroutinefunction(hook_function):
            await hook_function(message)
        else:
            hook_function(message)

    @staticmethod
    def _get_hook_function_for_message(
            message: W24TechreadMessage,
            hooks: List[Hook]
    ) -> Optional[Callable]:
        """ Get the hook function that corresponds to the message
        type.

        Arguments:
            message {W24TechreadMessage} -- Messsage returned from the
                read_drawing method

            hooks {List[Hook]} -- List of hooks from which we need to
                pick the suited one

        Returns:
            Optional[Callable] -- Hook function that should be called
        """

        # because we allow the user to define the ask in the hook,
        # we need to make some extra effort when filtering
        if message.message_type == W24TechreadMessageType.ASK:
            def hook_filter(hook: Hook) -> bool:
                return hook.ask is not None \
                    and message.message_subtype.value \
                    == hook.ask.ask_type.value

        # if the message is of any other type, we just need to
        # compare the the message_type and message_subtype
        else:
            def hook_filter(hook: Hook) -> bool:
                return hook.message_type is not None \
                    and hook.message_subtype is not None \
                    and message.message_type == hook.message_type \
                    and message.message_subtype == hook.message_subtype

        # return the first positive case
        for cur_hook in filter(hook_filter, hooks):
            return cur_hook.function

        # if we are still here, we have an unknown message type, which
        # probobly is being caused by an API update. We want to ensure
        # that the user is being informed, but we do not want to break
        # the existing functionality -> warning
        logger.warning(
            "Ignoring message of type %s:%s - no hook registered",  # noqa
            message.message_type,
            message.message_subtype)
        return None
