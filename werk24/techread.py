from __future__ import annotations

import io
import json
import ssl
import uuid
from asyncio import iscoroutinefunction
from io import BufferedReader
from typing import AsyncGenerator, Callable, Dict, List, Optional, Tuple, Union
from urllib.parse import urljoin

import aiohttp
import certifi
import websockets
from packaging.version import Version
from pydantic import UUID4, HttpUrl, ValidationError

from werk24 import (
    AskV2,
    EncryptionKeys,
    Hook,
    PresignedPost,
    TechreadAction,
    TechreadCommand,
    TechreadException,
    TechreadExceptionLevel,
    TechreadExceptionType,
    TechreadInitResponse,
    TechreadMessage,
    TechreadMessageType,
    TechreadRequest,
    TechreadWithCallbackPayload,
)
from werk24._version import __version__
from werk24.utils.crypt import decrypt_with_private_key, encrypt_with_public_key
from werk24.utils.defaults import Settings
from werk24.utils.exceptions import (
    BadRequestException,
    EncryptionException,
    InsufficientCreditsException,
    RequestTooLargeException,
    ResourceNotFoundException,
    ServerException,
    SSLCertificateError,
    UnauthorizedException,
    UnsupportedMediaType,
)
from werk24.utils.license import find_license
from werk24.utils.logger import get_logger

HTTP_EXCEPTION_CLASSES = {
    range(200, 300): None,
    range(400, 401): BadRequestException,
    range(401, 404): UnauthorizedException,
    range(404, 405): ResourceNotFoundException,
    range(413, 414): RequestTooLargeException,
    range(415, 416): UnsupportedMediaType,
    range(429, 430): InsufficientCreditsException,
    range(300, 400): ServerException,
    range(500, 600): ServerException,
    range(416, 500): ServerException,
}

EXCEPTION_MAP = {
    RequestTooLargeException: TechreadExceptionType.DRAWING_FILE_SIZE_TOO_LARGE,
    BadRequestException: TechreadExceptionType.DRAWING_FILE_SIZE_TOO_LARGE,
}

settings = Settings()
logger = get_logger(settings.log_level)


# Determine if the websockets library supports the `extra_headers` parameter.
# There was a breaking change in version 14.0 that changed the parameter name.
try:
    version = Version(websockets.__version__)
    USE_EXTRA_HEADERS = version < Version("14.0")
except Exception:
    USE_EXTRA_HEADERS = False


class Werk24Client:

    def __init__(
        self,
        wss_server=settings.wss_server,
        https_server=settings.http_server,
        token: Optional[str] = None,
        region: Optional[str] = None,
    ):
        self.license = find_license(token, region)
        self._wss_server = str(wss_server)
        self._https_server = str(https_server)
        self._wss_session = None

    def _get_auth_headers(self):
        """
        Get the authentication headers for the request.

        Returns:
        -------
        - dict: The authentication headers.
        """
        return {"Authorization": f"Token {self.license.token}"}

    def _create_websocket_session(
        self,
        wss_close_timeout: float = settings.wss_close_timeout,
    ):
        headers = self._get_auth_headers()
        if USE_EXTRA_HEADERS:
            return websockets.connect(
                self._wss_server,
                extra_headers=headers,
                close_timeout=wss_close_timeout,
            )
        return websockets.connect(
            self._wss_server,
            additional_headers=headers,
            close_timeout=wss_close_timeout,
        )

    async def __aenter__(self):
        try:
            self._wss_session = await self._create_websocket_session()
        except Exception as exc:
            logger.error("Failed to establish a connection with the server: %s", exc)
            raise ServerException(details=str(exc)) from exc
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        logger.debug(f"Exiting the session with the server {self._wss_server}")
        if self._wss_session is not None:
            await self._wss_session.close()

    async def read_drawing_with_hooks(
        self,
        drawing: Union[BufferedReader, bytes],
        hooks: list[Hook],
        max_pages: int = settings.max_pages,
        encryption_keys: Optional[EncryptionKeys] = None,
    ):

        asks_list = [cur_ask.ask for cur_ask in hooks if cur_ask.ask is not None]

        # send out the request and make a generator
        # that triggers when the result of an ask
        # becomes available
        async for message in self.read_drawing(
            drawing,
            asks_list,
            max_pages=max_pages,
            encryption_keys=encryption_keys,
        ):
            await self.call_hooks_for_message(message, hooks)

    async def read_drawing(
        self,
        drawing: Union[BufferedReader, bytes, io.BytesIO],
        asks: list[AskV2],
        max_pages: int = settings.max_pages,
        encryption_keys: Optional[EncryptionKeys] = None,
    ) -> AsyncGenerator[TechreadMessage, None, None]:
        """
        Read the drawing and return the extracted text.

        This function performs the following steps:
        1. Validates the input drawing.
        2. Sends an initiation request with the specified questions (`asks`).
        3. Uploads the drawing to the server.
        4. Signals the server to start reading the uploaded drawing.
        5. Yields messages as the process progresses.

        Args:
        ----
        - drawing (Union[BufferedReader, bytes]): The drawing to process.
        - asks (list[Ask]): A list of questions (asks) to provide context for reading.
        - max_pages (int, optional): Maximum number of pages to process.
            Defaults to `settings.max_pages`.
        - encryption_keys (Optional[EncryptionKeys], optional): Optional encryption
            keys for secure communication.

        Yields:
        ------
        - str: Progress or result messages during the drawing reading process.

        Raises:
        ------
        - BadRequestException: If the request is malformed.
        - RequestTooLargeException: If the drawing exceeds the maximum size limit.
        - Any other exceptions encountered will be logged and re-raised.
        """
        # Run the preflight checks
        self.run_preflight_checks(drawing)

        # Initiate the request
        init_message, init_response = await self.init_request(asks, max_pages)
        yield init_message
        logger.debug("Initialization request sent and response received.")

        # Check if the initialization response is successful
        if not init_response.is_successful:
            raise BadRequestException("Initialization request failed.")

        # Handle public key availability
        server_public_key = None
        if init_response.public_key:
            server_public_key = init_response.public_key.encode("utf-8")
            logger.info("Public key provided by the server.")
        else:
            logger.info(
                "No public key provided. Consider upgrading to a higher service level "
                "if end-to-end encryption is required."
            )

        # Upload the drawing file
        try:
            logger.debug("Uploading drawing file...")
            await self._upload_associated_file(
                init_response.drawing_presigned_post,
                drawing,
                public_server_key=server_public_key,
            )
            logger.debug("Drawing file uploaded successfully.")
        except (BadRequestException, RequestTooLargeException) as exc:
            logger.error("Error during drawing upload: %s", exc)
            async for message in self._trigger_asks_exception(asks, exc):
                yield message
            return

        # Notify the server to start reading the drawing
        try:
            async for message in self._send_command_read(encryption_keys):
                yield message
        except Exception as exc:
            logger.error("An error occurred while sending the read command: %s", exc)
            raise

    @staticmethod
    async def _trigger_asks_exception(
        asks: List[AskV2],
        exception_raw: Union[BadRequestException, RequestTooLargeException],
    ) -> AsyncGenerator[TechreadMessage, None]:
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
        exception = TechreadException(
            exception_level=TechreadExceptionLevel.ERROR,
            exception_type=exception_type,
        )

        # then yield one message for each of the requested asks
        for cur_ask in asks:
            yield TechreadMessage(
                request_id=uuid.uuid4(),
                message_type=TechreadMessageType.ASK,
                message_subtype=cur_ask.ask_type,
                exceptions=[exception],
            )

    async def init_request(
        self,
        asks: List[AskV2],
        max_pages: int,
    ) -> Tuple[TechreadMessage, TechreadInitResponse]:
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

        Raises:
        ------
        - ServerException: If the server returns an error response during
          initialization.

        """
        logger.debug("API method init_request() called")

        # Construct the techread request
        request = TechreadRequest(
            asks=asks,
            max_pages=max_pages,
        )

        # Send the initialization command to the server
        await self._send_command(
            TechreadAction.INITIALIZE.value,
            request.model_dump_json(),
        )
        logger.debug("Techread request submitted")

        # Wait for the server response
        message = await self._recv_message()
        logger.info("Received request_id %s", message.request_id)
        payload = message.payload_dict
        payload = TechreadInitResponse.model_validate(payload)

        return message, payload

    async def _recv_message(self) -> TechreadMessage:
        """
        Receive a message from the websocket and interpret the result as W24TechreadMessage

        Raises:
        ------
        - RuntimeError: When trying to send a command without having entered the profile.

        Returns:
        -------
        - W24TechreadMessage: interpreted message
        """

        # make sure that we have an AuthClient
        if self._wss_session is None:
            raise RuntimeError(
                "You need to call enter the profile before receiving command"
            )

        # wait for the websocket to say something and interpret the message
        message_raw = str(await self._wss_session.recv())
        logger.debug("Received message: %s", message_raw)
        message = self._parse_message(message_raw)
        return message

    async def _send_command(self, action: str, message: str = "{}") -> None:
        """
        Sends a command to the websocket.

        This method wraps the given action and message into a
        W24TechreadCommand object, serializes it to JSON, and sends it to the
        server via the websocket.

        Args:
        ----
        - action (str): The action requested by the client.
        - message (str, optional): Additional data to send along with the action.
            Defaults to "{}". It should be a JSON-encoded string for easy
            expansion.

        Raises:
        ------
        - RuntimeError: Raised if the method is called before initializing the
            profile (i.e., if the websocket session is not established).
        """
        logger.debug(f"Sending command with action {action}")

        # Ensure the websocket session is active
        if not self._wss_session:
            raise RuntimeError(
                "Profile entry is required before sending commands. "
                "Please call the appropriate method to enter the profile."
            )

        # Create the command object
        command = TechreadCommand(action=action, message=message)
        logger.debug("Sending command: %s", command.model_dump_json())

        # Send the serialized command to the websocket server
        await self._wss_session.send(command.model_dump_json())

    @staticmethod
    def _parse_message(message_raw: str) -> TechreadMessage:
        """
        Interpret the raw WebSocket message and convert it into a TechreadMessage.

        Args:
        ----
        - message_raw (str): The raw WebSocket message as a string.

        Raises:
        ------
        - UnauthorizedException: Raised when the requested action is forbidden
          or the user lacks the necessary privileges.
        - ServerException: Raised when the server's response is invalid or unexpected.

        Returns:
        -------
        - TechreadMessage: The interpreted and validated message.
        """
        logger.debug("Parsing raw message: %s", message_raw)
        try:
            # Attempt to validate the raw message against the TechreadMessage model
            return TechreadMessage.model_validate_json(message_raw)

        except ValidationError as exception:
            logger.warning(
                "Message validation failed. Attempting to parse error response."
            )

            # Try to interpret the raw message as a JSON object
            try:
                response = json.loads(message_raw)
            except json.JSONDecodeError as exception:
                raise ServerException(
                    f"Invalid JSON received: {message_raw}"
                ) from exception

            # Extract the error message from the parsed response
            error_message = response.get("message", "Unknown error")

            # Raise specific exceptions for known error messages
            if error_message == "Forbidden":
                raise UnauthorizedException(
                    "Requested action is forbidden"
                ) from exception

            # Raise a generic exception for unexpected server responses
            raise ServerException(
                f"Unexpected server response: {message_raw}"
            ) from exception

    async def _upload_associated_file(
        self,
        presigned_post: PresignedPost,
        content: Union[BufferedReader, bytes],
        public_server_key: Optional[bytes] = None,
    ):
        """
        Upload the associated file (drawing) to the server.

        Args:
        ----
        - presigned_post (dict): The presigned POST URL and fields.
        - drawing (Union[BufferedReader, bytes]): The drawing to upload.
        - public_server_key (Optional[bytes], optional): The server's public key for encryption.

        Raises:
        ------
        - BadRequestException: If the request is malformed.
        - RequestTooLargeException: If the drawing exceeds the maximum size limit.
        - Any other exceptions encountered will be logged and re-raised.
        """
        logger.debug("Starting the upload process for the associated file.")

        # ignore if payload is empty
        if content is None:
            raise UnsupportedMediaType("Drawing is empty")

        # Encrypt the content if the server's public key is provided
        if public_server_key:
            try:
                logger.debug("Encrypting the content using the server's public key.")
                content = encrypt_with_public_key(public_server_key, content)
            except Exception as exc:
                logger.error("Encryption failed: %s", exc)
                raise EncryptionException(
                    "Failed to encrypt the drawing with the server's public key."
                ) from exc

        # generate the form data by merging the presigned
        # fields with the file
        form = aiohttp.FormData({**presigned_post.fields, "file": content})

        try:
            logger.debug("Uploading file to the server: %s", str(presigned_post.url))
            async with self._make_https_session() as session:
                response = await session.post(str(presigned_post.url), data=form)
                self._raise_for_status(str(presigned_post.url), response.status)
            logger.info("File uploaded successfully.")
        except aiohttp.ClientConnectorCertificateError as exc:
            raise SSLCertificateError("SSL certificate error occurred.") from exc
        except Exception as exc:
            logger.error("File upload failed: %s", exc)
            raise

    @staticmethod
    def run_preflight_checks(drawing: Union[BufferedReader, bytes]):
        # quickly check whether the input type is bytes. If it is string,
        # the presigned-AWS post interestingly returns a 403 error_code
        # without additional information. We want to inform the caller
        # that they submitted the wrong data type.
        # See Github Issue #13
        if not isinstance(drawing, (BufferedReader, bytes, io.BytesIO)):
            logger.warning("Unsupported media type for drawing")
            raise UnsupportedMediaType(
                "Drawing bytes requires 'bytes' or 'BufferedReader' type"
            )

    @staticmethod
    def _get_hook_function_for_message(
        message: TechreadMessage, hooks: List[Hook]
    ) -> Optional[Callable]:
        """
        Retrieve the appropriate hook function for a given message.

        This method determines which hook function should be invoked based on the
        message type and subtype. If no matching hook is found, it logs a warning
        and returns `None`.

        Args:
        ----
        - message (TechreadMessage): The message returned from the `read_drawing` method.
        - hooks (List[Hook]): A list of available hooks to evaluate.

        Returns:
        -------
        - Optional[Callable]: The hook function to invoke, or `None` if no suitable
          hook is found.
        """
        logger.debug(
            "Evaluating hooks for message type: %s, subtype: %s",
            message.message_type,
            message.message_subtype,
        )

        def hook_filter(hook: Hook) -> bool:
            """
            Determine if a hook matches the given message.

            Args:
            ----
            - hook (Hook): A hook to evaluate.

            Returns:
            -------
            - bool: True if the hook matches the message; otherwise, False.
            """
            # Special handling for ASK message types
            if message.message_type == TechreadMessageType.ASK:
                return (
                    hook.ask is not None
                    and hook.ask.ask_type.value == message.message_subtype.value
                )

            # General handling for other message types
            return (
                hook.message_type == message.message_type
                and hook.message_subtype == message.message_subtype
            )

        # Find and return the first matching hook's function
        for cur_hook in filter(hook_filter, hooks):
            logger.debug(
                "Hook function matched for message type: %s, subtype: %s",
                message.message_type,
                message.message_subtype,
            )
            return cur_hook.function

        return None

    async def call_hooks_for_message(
        self,
        message: TechreadMessage,
        hooks: List[Hook],
    ) -> None:
        """
        Invoke the appropriate hook function for the given response message.

        This method determines the correct hook function for the provided message and
        invokes it.If the hook function is asynchronous, it will be awaited. If it is
        synchronous, it will be called directly.

        Args:
        ----
        - message (TechreadMessage): The message returned from the `read_drawing` method.
        - hooks (List[Hook]): A list of hooks to evaluate and select the appropriate one.

        Raises:
        ------
        - ServerException: If the server returns an ERROR message.
        """
        logger.debug(
            "call_hooks_for_message() invoked for message_type: %s",
            message.message_type,
        )

        # Retrieve the appropriate hook function for the given message
        hook_function = self._get_hook_function_for_message(message, hooks)
        if hook_function is None:
            logger.debug(
                "No suitable hook function found for message_type: %s",
                message.message_type,
            )
            return

        # Warn if the hook function is not callable
        if not callable(hook_function):
            logger.warning(
                "Registered hook for message_type '%s' is not callable. "
                "Ensure the hook is a Callable (e.g., a function or lambda).",
                message.message_type,
            )
            return

        # Invoke the hook function asynchronously or synchronously
        try:
            if iscoroutinefunction(hook_function):
                logger.debug(
                    "Invoking asynchronous hook for message_type: %s",
                    message.message_type,
                )
                await hook_function(message)
            else:
                logger.debug(
                    "Invoking synchronous hook for message_type: %s",
                    message.message_type,
                )
                hook_function(message)
            logger.debug(
                "Hook function executed successfully for message_type: %s",
                message.message_type,
            )

        except Exception as exc:
            logger.error(
                "Error while invoking hook for message_type '%s': %s",
                message.message_type,
                exc,
            )
            raise

    async def read_drawing_with_callback(
        self,
        drawing: Union[BufferedReader, bytes],
        asks: List[AskV2],
        callback_url: str,
        max_pages: int = 5,
        drawing_filename: Optional[str] = None,
        callback_headers: Optional[Dict[str, str]] = None,
        public_key: Optional[bytes] = None,
    ) -> UUID4:
        """
        Read the drawing and register a callback URL.

        This method initializes the reading process and registers a callback URL
        that the server will use to send message responses asynchronously.

        Args:
        ----
        - drawing (Union[BufferedReader, bytes]): The drawing to process.
        - asks (List[W24Ask]): List of requests specifying the desired information.
        - callback_url (str): URL to receive the callback requests.
        - max_pages (int, optional): Maximum number of pages to process. Defaults to 5.
        - drawing_filename (Optional[str], optional): Optional filename of the drawing.
          Defaults to None.
        - callback_headers (Optional[Dict[str, str]], optional): Optional headers for
          the callback request. Defaults to None.
        - public_key (Optional[bytes], optional): Optional public key for encrypting
          the callback request.

        Raises:
        ------
        - ServerException: Raised when the server returns an error message.
        - InsufficientCreditsException: Raised when the user lacks sufficient credits
          for the request.
        - ValueError: Raised if the drawing or callback_url is invalid.

        Returns:
        -------
        - UUID4: The request ID of the registered request.
        """
        logger.debug("API method read_drawing_with_callback() called")

        # send the request to the API

        # Set a default drawing filename if none is provided
        drawing_filename = drawing_filename or "drawing.pdf"
        logger.debug("Drawing filename: %s", drawing_filename)

        # validate the payload locally. This is not strictly necessary
        # but it is a good way to catch errors early.
        payload = TechreadWithCallbackPayload(
            asks=asks,
            callback_url=callback_url,
            callback_headers=callback_headers,
            max_pages=max_pages,
            client_version=__version__,
            public_key=public_key,
        )

        # create the form data
        data = aiohttp.FormData()
        data.add_field("drawing", drawing, filename=drawing_filename)
        for key, value in payload.model_dump(mode="json").items():
            data.add_field(key, json.dumps(value))

        # send the request
        headers = self._get_auth_headers()
        url = self._make_https_url("/techread/read-with-callback")
        async with self._make_https_session() as session:
            response = await session.post(url, data=data, headers=headers)
            self._raise_for_status(url, response.status)
            response_json = await response.json(content_type=None)

        try:
            return uuid.UUID(response_json["request_id"])
        except (ValueError, KeyError) as e:
            raise BadRequestException(f"Request failed: {response_json}") from e

    def _make_https_url(self, endpoint: str) -> str:
        """
        Create a full HTTPS URL for the given endpoint.

        Args:
        ----
        - endpoint (str): The API endpoint to append to the base URL.

        Returns:
        -------
        - str: The full URL for the HTTPS request.
        """
        return urljoin(self._https_server, endpoint)

    def _make_https_session(
        self, timeout_seconds: int = 30, cafile: str = None
    ) -> aiohttp.ClientSession:
        """
        Create a configured aiohttp.ClientSession with SSL context and timeouts.

        Args:
        ----
        - timeout_seconds (int): Timeout in seconds for socket connection and read
          operations.
        - cafile (str, optional): Path to the Certificate Authority file.
          Defaults to certifi's CA bundle.

        Returns:
        -------
        - aiohttp.ClientSession: A configured HTTP client session.
        """
        try:
            # Use the provided CA file or the default certifi CA bundle
            cafile = cafile or certifi.where()
            ssl_context = ssl.create_default_context(cafile=cafile)
            connector = aiohttp.TCPConnector(ssl=ssl_context)

            # Configure timeouts
            timeout = aiohttp.ClientTimeout(
                total=None,
                sock_connect=timeout_seconds,
                sock_read=timeout_seconds,
            )

            # Return the configured session
            return aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
            )
        except Exception as e:
            # Log the error and re-raise
            logger.exception("Failed to create aiohttp.ClientSession: %s", e)
            raise

    @staticmethod
    def _raise_for_status(url: str, status_code: int) -> None:
        """
        Raise the correct exception based on the HTTP status code.

        Args:
        ----
        - url (str): The requested URL.
        - status_code (int): The received response status code.

        Raises:
        ------
        - BadRequestException: When the request body cannot be interpreted.
        - UnauthorizedException: When the token or requested file has expired.
        - ResourceNotFoundException: When the endpoint does not exist.
        - RequestTooLargeException: When the request exceeds the size limit (413).
        - UnsupportedMediaTypeException: When the file's media type is not supported.
        - ServerException: For all other non-2xx status codes.
        - InsufficientCreditsException: When the user does not have enough credits.
        """
        # Log the status code for all responses
        logger.debug(
            "Processing response from '%s' with status code %s", url, status_code
        )

        # No exception for successful responses (2xx)
        if 200 <= status_code < 300:
            logger.info(
                "Request to '%s' succeeded with status code %s", url, status_code
            )
            return

        # Handle known exceptions based on the HTTP status code
        exception_class = next(
            (
                exc
                for codes, exc in HTTP_EXCEPTION_CLASSES.items()
                if status_code in codes
            ),
            None,
        )

        if exception_class:
            logger.warning(
                "Request to '%s' failed with status code %s. Raising %s.",
                url,
                status_code,
                exception_class.__name__,
            )
            raise exception_class(f"Request failed '{url}' with code {status_code}")

        # Fallback for unhandled status codes
        logger.error(
            "Request to '%s' failed with unhandled status code %s.", url, status_code
        )
        raise ServerException(f"Request failed '{url}' with code {status_code}")

    async def _send_command_read(
        self,
        client_public_key_pem: Optional[bytes] = None,
        client_private_key_pem: Optional[bytes] = None,
        client_private_key_passphrase: Optional[bytes] = None,
        max_messages_per_session: int = 100,
    ) -> AsyncGenerator[TechreadMessage, None]:
        """
        Send a techread request to the backend and yield resulting messages.

        Args:
            client_public_key_pem (Optional[bytes]): PEM-encoded public key, if applicable.
            client_private_key_pem (Optional[bytes]): PEM-encoded private key, if applicable.
            client_private_key_passphrase (Optional[bytes]): Passphrase for the private key, if applicable.

        Yields:
            W24TechreadMessage: The received messages, processed as needed.
        """
        logger.debug("API method _send_command_read() called")

        # Prepare the initial request message
        message = {}
        if client_public_key_pem:
            message["public_key"] = client_public_key_pem.decode("utf-8")
            logger.debug("Public key added to message")

        # Submit the request to the API
        logger.debug("Submitting techread request with payload: %s", message)
        try:
            await self._send_command(
                TechreadAction.READ.value,
                json.dumps(message),
            )
            logger.info("Techread request successfully submitted")
        except Exception as e:
            logger.error("Failed to submit techread request: %s", e)
            raise

        # Listen for incoming messages from the server
        logger.debug("Listening for responses from the server")
        try:
            for _ in range(max_messages_per_session):
                try:
                    raw_message = str(await self._wss_session.recv())
                except (
                    websockets.exceptions.ConnectionClosedError,
                    websockets.exceptions.ConnectionClosedOK,
                ):
                    break

                message = self._parse_message(raw_message)
                logger.info(
                    "Received message type: %s, subtype: %s",
                    message.message_type,
                    message.message_subtype,
                )

                # If there's a payload URL, download the associated payload
                if message.payload_url:
                    logger.debug(
                        "Downloading payload from URL: %s", message.payload_url
                    )
                    try:
                        message.payload_bytes = await self.download_payload(
                            message.payload_url,
                            client_private_key_pem,
                            client_private_key_passphrase,
                        )
                        logger.debug("Payload successfully downloaded")
                    except Exception as e:
                        logger.error("Failed to download payload: %s", e)
                        raise

                # Yield the message for immediate consumption
                yield message

        except Exception as e:
            logger.error("Error occurred while processing responses: %s", e)
            raise

    async def download_payload(
        self,
        payload_url: HttpUrl,
        client_private_key_pem: Optional[bytes],
        client_private_key_passphrase: Optional[bytes] = None,
    ) -> bytes:
        """
        Download the payload from the server.

        Args:
        ----
        - payload_url (HttpUrl): The URL of the payload.
        - client_private_key_pem (Optional[bytes]): PEM-encoded private key, if decryption is needed.
        - client_private_key_passphrase (Optional[bytes]): Passphrase for the private key, if applicable.

        Raises:
        ------
        - RuntimeError: Raised for untrusted payload sources to prevent payload injection or token theft.
        - BadRequestException: Raised if the request body cannot be interpreted.
        - UnauthorizedException: Raised if the token or requested file has expired.
        - ResourceNotFoundException: Raised if the endpoint does not exist.
        - RequestTooLargeException: Raised if the payload exceeds size limits (status code 413).
        - UnsupportedMediaTypeException: Raised if the file's media type is unsupported.
        - ServerException: Raised for all other non-2xx status codes.

        Returns:
        -------
        - bytes: The payload, either decrypted or raw.
        """
        logger.debug("Starting payload download from %s", payload_url)

        # Attempt to download the payload
        try:
            async with self._make_https_session() as session:
                logger.debug("Sending GET request to %s", payload_url)
                response = await session.get(str(payload_url))

                # Raise appropriate exceptions based on response status
                self._raise_for_status(payload_url, response.status)

                raw_payload = await response.content.read()
                logger.info("Payload successfully downloaded from %s", payload_url)

        except (
            UnauthorizedException,
            RequestTooLargeException,
            ServerException,
            BadRequestException,
            ResourceNotFoundException,
        ) as known_exception:
            logger.error(
                "Known exception occurred while downloading payload from %s: %s",
                payload_url,
                known_exception,
            )
            raise
        except Exception as unexpected_exception:
            logger.exception(
                "Unexpected error occurred during payload download from %s", payload_url
            )
            raise ServerException(
                f"Unexpected error while downloading payload from {payload_url}"
            ) from unexpected_exception

        # Decrypt payload if private key is provided
        if client_private_key_pem:
            logger.debug("Decrypting the payload using the provided private key")
            try:
                return decrypt_with_private_key(
                    client_private_key_pem,
                    client_private_key_passphrase,
                    raw_payload,
                )
            except Exception as e:
                logger.error("Failed to decrypt the payload: %s", e)
                raise RuntimeError("Failed to decrypt the payload.") from e

        logger.debug("Returning the raw payload as no decryption was required")
        return raw_payload
