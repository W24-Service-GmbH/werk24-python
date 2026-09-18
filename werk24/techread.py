from __future__ import annotations

import asyncio
import functools
import io
import ipaddress
import json
import re
import ssl
import uuid
from asyncio import iscoroutinefunction
from collections import deque
from functools import lru_cache
from io import BufferedReader
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional, Tuple, Union
from urllib.parse import urljoin, urlparse

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
    SystemStatus,
    TechreadAction,
    TechreadCommand,
    TechreadException,
    TechreadExceptionLevel,
    TechreadExceptionType,
    TechreadInitResponse,
    TechreadMessage,
    TechreadMessageSubtype,
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
    InvalidPriorityError,
    PriorityTooHighError,
    RequestTooLargeException,
    ResourceNotFoundException,
    ServerException,
    SSLCertificateError,
    UnauthorizedException,
    UnsupportedMediaType,
)
from werk24.utils.license import find_license
from werk24.utils.logger import get_logger
from werk24.utils.priority import validate_priority

#: How many bytes of a refusal body to read before giving up on finding a
#: reason in it. S3's error documents are a few hundred bytes; anything past
#: this is not one, and reading it on an already-failing path buys nothing.
#: This bounds the read itself, not just the search, so a body that is large
#: or never ends costs one bounded allocation and no wait for EOF.
_S3_ERROR_BODY_LIMIT = 4096

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


@lru_cache(maxsize=1)
def _default_ssl_context() -> ssl.SSLContext:
    """Return a shared SSL context built from the certifi CA bundle.

    Building an SSL context reads and parses the CA bundle from disk, which is
    relatively expensive (tens of milliseconds). Caching it avoids paying that
    cost on every HTTPS request.
    """
    return ssl.create_default_context(cafile=certifi.where())


@lru_cache(maxsize=1)
def _all_valid_ask_types() -> frozenset:
    """Return the set of all valid ask-type values (API v1 and v2).

    Computed once and cached; the enum membership never changes at runtime.
    """
    # Imported lazily to avoid a circular import at module load time.
    from werk24.models.v1.ask import W24AskType
    from werk24.models.v2.enums import AskType

    return frozenset(ask_type.value for ask_type in W24AskType) | frozenset(
        ask_type.value for ask_type in AskType
    )


# Determine if the websockets library supports the `extra_headers` parameter.
# There was a breaking change in version 14.0 that changed the parameter name.
try:
    version = Version(websockets.__version__)
    USE_EXTRA_HEADERS = version < Version("14.0")
except Exception:
    USE_EXTRA_HEADERS = False

# Import websockets exceptions - they moved in version 14.0
try:
    from websockets.exceptions import (
        ConnectionClosedError,
        ConnectionClosedOK,
        InvalidStatus,
    )
except ImportError:
    # websockets 14+ moved exceptions to the main module
    from websockets import (
        ConnectionClosedError,
        ConnectionClosedOK,
        InvalidStatus,
    )


def _closes_standalone_session(method):
    """Close the pooled HTTPS session when the call was made on a bare client.

    The HTTPS-only methods are documented as usable without
    ``async with Werk24Client()``, and such a caller never reaches
    ``__aexit__``. Before pooling, each of those calls built and closed its own
    session; after pooling, nothing would close it and aiohttp warns about the
    unclosed session when the client is collected.

    Inside the context this is a no-op and the session stays pooled across
    every call, which is the whole point of pooling it.
    """

    @functools.wraps(method)
    async def _wrapper(self, *args, **kwargs):
        try:
            return await method(self, *args, **kwargs)
        finally:
            await self._release_https_if_standalone()

    return _wrapper


class Werk24Client:

    def __init__(
        self,
        wss_server=settings.wss_server,
        https_server=settings.http_server,
        token: Optional[str] = None,
        region: Optional[str] = None,
        ping_interval: float = 30.0,
        ping_timeout: float = 10.0,
        max_reconnect_attempts: int = 3,
        reconnect_delay: float = 1.0,
    ):
        self.license = find_license(token, region)
        self._wss_server = str(wss_server)
        self._https_server = str(https_server)
        self._wss_session = None
        # Reuse a single SSL context configured with the certifi CA bundle
        # to avoid recreating it for each connection and to ensure that the
        # certificate chain is properly verified. The context is cached at
        # module level and shared across clients.
        self._ssl_context = _default_ssl_context()

        # One pooled HTTPS session for this client's lifetime. Built on first
        # use by _https_session(), closed by _graceful_shutdown(). See that
        # method for why it is not one session per call.
        self._shared_https_session: Optional[aiohttp.ClientSession] = None

        # Whether the caller is inside ``async with``. The HTTPS-only methods
        # (read_drawing_with_callback, download_payload, get_system_status)
        # are documented as usable on a bare client, and such a caller never
        # reaches __aexit__ - so nothing would close the pooled session and
        # aiohttp would warn about it on collection. Outside the context the
        # session is closed when the call that built it returns, which is the
        # per-call behaviour those methods had before pooling.
        self._entered = False

        # WebSocket connection management
        self._ping_interval = ping_interval
        self._ping_timeout = ping_timeout
        self._max_reconnect_attempts = max_reconnect_attempts
        self._reconnect_delay = reconnect_delay
        self._is_shutting_down = False
        self._reconnect_attempts = 0

    @staticmethod
    def validate_asks(asks: List[AskV2]) -> None:
        """
        Validate ask types before sending request to the API.

        This method checks if all provided ask types are valid according to either
        API v1 (W24AskType) or API v2 (AskType) specifications. It raises a
        BadRequestException with helpful error messages if invalid ask types are found.

        Parameters
        ----------
        asks : List[AskV2]
            List of ask types to validate. Can be W24Ask (v1) or AskV2 (v2) objects.

        Raises
        ------
        BadRequestException
            If any ask types are invalid, with a message listing the invalid types
            and all valid ask types.

        Examples
        --------
        >>> from werk24.models.v1.ask import W24AskVariantMeasures
        >>> from werk24.models.v2.asks import AskBalloons
        >>> asks = [W24AskVariantMeasures(), AskBalloons()]
        >>> Werk24Client.validate_asks(asks)  # No exception raised

        >>> from pydantic import BaseModel
        >>> class InvalidAsk(BaseModel):
        ...     ask_type = "INVALID_TYPE"
        >>> Werk24Client.validate_asks([InvalidAsk()])  # Raises BadRequestException
        """
        if not asks:
            raise BadRequestException(
                "No ask types provided. At least one ask type is required."
            )

        # Get all valid ask types from both versions (cached at module level).
        all_valid_types = _all_valid_ask_types()

        # Extract and validate ask type names from the input
        invalid_asks = []
        for ask in asks:
            # Get the ask_type attribute
            ask_type_value = getattr(ask, "ask_type", None)

            if ask_type_value is None:
                invalid_asks.append("(missing ask_type)")
                continue

            # Convert enum to string if needed
            if hasattr(ask_type_value, "value"):
                ask_type_str = ask_type_value.value
            else:
                ask_type_str = str(ask_type_value)

            # Check if the ask type is valid
            if ask_type_str not in all_valid_types:
                invalid_asks.append(ask_type_str)

        if invalid_asks:
            # Create helpful error message
            sorted_valid_types = sorted(all_valid_types)
            error_msg = (
                f"Invalid ask type(s): {', '.join(invalid_asks)}. "
                f"Valid ask types are: {', '.join(sorted_valid_types)}"
            )
            raise BadRequestException(error_msg)

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
                ssl=self._ssl_context,
                ping_interval=self._ping_interval,
                ping_timeout=self._ping_timeout,
            )
        return websockets.connect(
            self._wss_server,
            additional_headers=headers,
            close_timeout=wss_close_timeout,
            ssl=self._ssl_context,
            ping_interval=self._ping_interval,
            ping_timeout=self._ping_timeout,
        )

    async def _reconnect(self):
        """
        Attempt to reconnect the WebSocket connection.

        This method is called when the connection is lost or becomes unresponsive.
        It closes the existing connection and attempts to establish a new one.

        Raises:
        ------
        - ServerException: If reconnection fails after all retry attempts.
        """
        if self._is_shutting_down:
            logger.debug("Skipping reconnect during shutdown")
            return

        logger.info("Attempting to reconnect WebSocket")

        # Close existing connection if any
        if self._wss_session:
            try:
                await self._wss_session.close()
            except Exception as exc:
                logger.debug("Error closing old connection: %s", exc)

        # Attempt to reconnect with retry logic
        try:
            await self._connect_with_retry()
        except Exception as exc:
            logger.error("Failed to reconnect: %s", exc)
            raise

    async def __aenter__(self):
        self._entered = True
        await self._connect_with_retry()
        return self

    def _https_session(self) -> aiohttp.ClientSession:
        """The one HTTPS session this client uses for its lifetime.

        Every HTTPS call - the drawing upload, read-with-callback, and each
        payload download - used to build its own ``ClientSession`` and
        ``TCPConnector``. The SSL *context* was cached; the *connection* was
        not, so a three-ask read paid three separate DNS, TCP and TLS
        handshakes to S3, strictly serialised, each one blocking receipt of
        the next ASK message.

        One session keeps aiohttp's connection pool alive across all of them.
        It is built on first use rather than in ``__aenter__`` because a
        client may be used for HTTPS without ever entering the WebSocket
        context, and closed in ``_graceful_shutdown``.
        """
        if self._shared_https_session is None or self._shared_https_session.closed:
            self._shared_https_session = self._make_https_session()
        return self._shared_https_session

    async def _connect_with_retry(self):
        """
        Establish WebSocket connection with retry logic.

        Raises:
        ------
        - UnauthorizedException: If authentication fails (403).
        - ServerException: If connection fails after all retry attempts.
        """
        self._reconnect_attempts = 0

        while self._reconnect_attempts < self._max_reconnect_attempts:
            try:
                self._wss_session = await self._create_websocket_session()
                self._reconnect_attempts = 0  # Reset on successful connection
                logger.info("WebSocket connection established successfully")
                return

            # -----------------------------------------------------------
            # Handle the error codes
            # -----------------------------------------------------------
            except InvalidStatus as exc:
                match exc.response.status_code:
                    case 403:
                        raise UnauthorizedException(
                            "Invalid status when connecting to the server"
                        ) from exc

                    case _:
                        raise ServerException(
                            f"Invalid status when connecting to the server: {exc.response.status_code}"
                        ) from exc

            # -----------------------------------------------------------
            # Handle remaining exceptions
            # -----------------------------------------------------------
            except Exception as exc:
                self._reconnect_attempts += 1
                if self._reconnect_attempts >= self._max_reconnect_attempts:
                    logger.error(
                        "Failed to establish connection after %d attempts: %s",
                        self._max_reconnect_attempts,
                        exc,
                    )
                    raise ServerException(details=str(exc)) from exc

                # Exponential backoff
                delay = self._reconnect_delay * (2 ** (self._reconnect_attempts - 1))
                logger.warning(
                    "Connection attempt %d/%d failed, retrying in %.1fs: %s",
                    self._reconnect_attempts,
                    self._max_reconnect_attempts,
                    delay,
                    exc,
                )
                await asyncio.sleep(delay)

    async def __aexit__(self, exc_type, exc_value, traceback):
        self._entered = False
        await self._graceful_shutdown()

    async def close(self) -> None:
        """Release everything this client holds.

        ``async with Werk24Client()`` does this on the way out, so most
        callers never need it. It exists for the caller who uses only the
        HTTPS-only methods on a bare client and wants to close explicitly
        rather than rely on the per-call release those methods do.

        Idempotent: closing a client that holds nothing is a no-op.
        """
        await self._graceful_shutdown()

    async def _close_https_session(self) -> None:
        """Close the pooled HTTPS session, if one was built."""
        if self._shared_https_session is None:
            return
        try:
            await self._shared_https_session.close()
        except Exception as exc:  # noqa: BLE001 - a close never fails a call
            logger.warning("Error during HTTPS session close: %s", exc)
        finally:
            self._shared_https_session = None

    async def _release_https_if_standalone(self) -> None:
        """Close the pooled session when there is no context to close it.

        Called from the HTTPS-only public methods. Inside ``async with`` this
        does nothing and the session stays pooled across every call, which is
        the point of pooling it. Outside it, there is no ``__aexit__`` coming,
        so the session is closed here rather than left for aiohttp to
        complain about.
        """
        if not self._entered:
            await self._close_https_session()

    async def _graceful_shutdown(self):
        """
        Perform graceful shutdown of WebSocket connection.

        This method:
        1. Sets shutdown flag to prevent reconnection
        2. Closes WebSocket connection cleanly
        """
        logger.debug(f"Starting graceful shutdown for server {self._wss_server}")
        self._is_shutting_down = True

        # Close WebSocket connection
        if self._wss_session is not None:
            try:
                await self._wss_session.close()
                logger.info("WebSocket connection closed successfully")
            except Exception as exc:
                logger.warning("Error during WebSocket close: %s", exc)

        # Close the pooled HTTPS session. Leaving it open would leak the
        # connector and emit aiohttp's "Unclosed client session" warning for
        # every client the caller discards.
        await self._close_https_session()

    async def read_drawing_with_hooks(
        self,
        drawing: Union[BufferedReader, bytes],
        hooks: list[Hook],
        max_pages: int = settings.max_pages,
        encryption_keys: Optional[EncryptionKeys] = None,
        priority: Optional[str] = None,
    ):
        """
        Read the drawing and call hooks for each message.

        This method extracts asks from hooks and processes the drawing.
        Ask validation is performed by the read_drawing method.

        Args:
        ----
        - drawing (Union[BufferedReader, bytes]): The drawing to process.
        - hooks (list[Hook]): List of hooks to call for each message.
        - max_pages (int, optional): Maximum number of pages to process.
        - encryption_keys (Optional[EncryptionKeys], optional): Optional encryption keys.
        - priority (Optional[str], optional): Optional priority level for the request.
            Valid values are "PRIO1", "PRIO2", "PRIO3" (case-insensitive).
            If not specified, the account's default tier is used.

        Raises:
        ------
        - BadRequestException: If ask types are invalid.
        - InvalidPriorityError: If the priority value is invalid.
        """
        asks_list = [cur_ask.ask for cur_ask in hooks if cur_ask.ask is not None]

        # send out the request and make a generator
        # that triggers when the result of an ask
        # becomes available
        async for message in self.read_drawing(
            drawing,
            asks_list,
            max_pages=max_pages,
            encryption_keys=encryption_keys,
            priority=priority,
        ):
            await self.call_hooks_for_message(message, hooks)

    async def read_drawing(
        self,
        drawing: Union[BufferedReader, bytes, io.BytesIO],
        asks: list[AskV2],
        max_pages: int = settings.max_pages,
        encryption_keys: Optional[EncryptionKeys] = None,
        priority: Optional[str] = None,
    ) -> AsyncGenerator[TechreadMessage, None, None]:
        """
        Read the drawing and return the extracted text.

        This function performs the following steps:
        1. Validates the input drawing.
        2. Validates the ask types.
        3. Validates the priority (if provided).
        4. Sends an initiation request with the specified questions (`asks`).
        5. Uploads the drawing to the server.
        6. Signals the server to start reading the uploaded drawing.
        7. Yields messages as the process progresses.

        Args:
        ----
        - drawing (Union[BufferedReader, bytes]): The drawing to process.
        - asks (list[AskV2]): A list of questions (asks) to provide context for reading.
        - max_pages (int, optional): Maximum number of pages to process.
            Defaults to `settings.max_pages`.
        - encryption_keys (Optional[EncryptionKeys], optional): Optional encryption
            keys for secure communication.
        - priority (Optional[str], optional): Optional priority level for the request.
            Valid values are "PRIO1", "PRIO2", "PRIO3" (case-insensitive).
            If not specified, the account's default tier is used.

        Yields:
        ------
        - str: Progress or result messages during the drawing reading process.

        Raises:
        ------
        - BadRequestException: If the request is malformed or ask types are invalid.
        - RequestTooLargeException: If the drawing exceeds the maximum size limit.
        - InvalidPriorityError: If the priority value is invalid.
        - Any other exceptions encountered will be logged and re-raised.
        """
        # Run the preflight checks
        self.run_preflight_checks(drawing)

        # Validate ask types before sending request
        self.validate_asks(asks)

        # Validate priority before sending request
        validated_priority = validate_priority(priority)

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
            # Unpack encryption keys if provided
            client_public_key_pem = None
            client_private_key_pem = None
            client_private_key_passphrase = None
            if encryption_keys:
                client_public_key_pem = encryption_keys.client_public_key_pem
                client_private_key_pem = encryption_keys.client_private_key_pem
                client_private_key_passphrase = (
                    encryption_keys.client_private_key_passphrase
                )

            async for message in self._send_command_read(
                client_public_key_pem=client_public_key_pem,
                client_private_key_pem=client_private_key_pem,
                client_private_key_passphrase=client_private_key_passphrase,
                priority=validated_priority,
            ):
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

        try:
            # wait for the websocket to say something and interpret the message
            message_raw = str(await self._wss_session.recv())
            logger.debug("Received message: %s", message_raw)
            message = self._parse_message(message_raw)
            return message
        except (
            ConnectionClosedError,
            ConnectionClosedOK,
        ) as exc:
            # The request/response exchange is stateful: the pending response is
            # bound to the connection it was requested on. Transparently
            # reconnecting and calling recv() again on a fresh connection would
            # block forever (no message is in flight on the new socket), so we
            # surface the failure instead and let the caller restart the whole
            # operation from INITIALIZE.
            logger.warning("Connection closed while receiving message: %s", exc)
            if self._is_shutting_down:
                raise
            raise ServerException(
                details=(
                    "The connection to the server was closed while awaiting a "
                    f"response: {exc}"
                )
            ) from exc

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

        try:
            # Send the serialized command to the websocket server
            await self._wss_session.send(command.model_dump_json())
        except (
            ConnectionClosedError,
            ConnectionClosedOK,
        ) as exc:
            logger.warning("Connection closed while sending command: %s", exc)
            if not self._is_shutting_down:
                await self._reconnect()
                # Retry sending after reconnect
                await self._wss_session.send(command.model_dump_json())
            else:
                raise

    @staticmethod
    def _priority_exception(
        payload: Any,
        requested_priority: Optional[str] = None,
    ) -> Optional[Union[PriorityTooHighError, InvalidPriorityError]]:
        """Return the typed exception for a priority refusal, or None.

        crew-api answers every refusal with the same envelope -- ``code``,
        ``message``, ``details``, ``request_id`` -- and never with a top-level
        ``error`` key. Both priority refusals are identified from that
        envelope:

        - 403 whose ``details`` name ``account_tier`` and
          ``requested_priority`` is the entitlement refusal. Both keys are
          required so an ordinary 403 is not mistaken for one.
        - ``details.error == "INVALID_PRIORITY"`` is the unparseable value,
          which the API sets explicitly for exactly this purpose.

        The older top-level ``error`` form is still accepted, so a client
        running against a server that emits it keeps its typed exceptions.

        Args:
        ----
        - payload (Any): The decoded error body. Anything that is not a
          mapping is not a refusal we recognise.
        - requested_priority (Optional[str]): The priority this client sent,
          where the caller knows it. Used to fill in ``invalid_value`` when
          the server does not name the offending value itself.

        Returns:
        -------
        - Optional[Union[PriorityTooHighError, InvalidPriorityError]]: The
          exception to raise, or None if this is not a priority refusal.
        """
        if not isinstance(payload, dict):
            return None

        details = payload.get("details")
        if not isinstance(details, dict):
            details = {}

        message = payload.get("message", "Unknown error")
        code = str(payload.get("code", ""))
        error_type = payload.get("error")

        if error_type == "PRIORITY_TOO_HIGH" or (
            code == "403"
            and "account_tier" in details
            and "requested_priority" in details
        ):
            return PriorityTooHighError(
                details=message,
                account_tier=details.get("account_tier"),
                requested_priority=details.get("requested_priority"),
            )

        if (
            error_type == "INVALID_PRIORITY"
            or details.get("error") == "INVALID_PRIORITY"
        ):
            # The current envelope names the offending value only in the
            # prose of ``message``. Take it from the older form's
            # ``details.priority`` when the server supplies it, otherwise from
            # what this client actually sent. It is never inferred from the
            # message text: that is prose meant for a human, and parsing it
            # would break the moment the wording changed.
            return InvalidPriorityError(
                details=message,
                invalid_value=details.get("priority", requested_priority),
            )

        return None

    @classmethod
    async def _raise_for_priority_error(
        cls,
        response: Any,
        requested_priority: Optional[str] = None,
    ) -> None:
        """Raise the typed exception if *response* is a priority refusal.

        ``_raise_for_status`` is handed the status code and nothing else, so
        by itself it answers a priority refusal on the HTTPS paths with a bare
        ``BadRequestException`` or ``UnauthorizedException`` and drops the
        tiers the server named -- even though ``read_drawing_with_callback``
        documents both typed exceptions. Read the body first; anything that is
        not a priority refusal falls through to the status-code mapping
        unchanged.

        Args:
        ----
        - response (Any): The aiohttp response to inspect.
        - requested_priority (Optional[str]): The priority this request sent,
          used to describe an ``InvalidPriorityError`` the server does not
          name a value for.

        Raises:
        ------
        - PriorityTooHighError: When the requested priority exceeds the
          account tier (403).
        - InvalidPriorityError: When the priority value is invalid (400).
        """
        if response.status not in (400, 403):
            return

        try:
            payload = await response.json(content_type=None)
        except (ValueError, aiohttp.ClientError):
            # A body we cannot decode is not one we can interpret. Leave it to
            # the status-code mapping rather than masking it.
            return

        exception = cls._priority_exception(payload, requested_priority)
        if exception is not None:
            raise exception

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
        - PriorityTooHighError: Raised when the requested priority exceeds the
          account tier (403 PRIORITY_TOO_HIGH).
        - InvalidPriorityError: Raised when the priority value is invalid
          (400 INVALID_PRIORITY).
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

            error_message = response.get("message", "Unknown error")

            # Handle both priority refusals (403 PRIORITY_TOO_HIGH and
            # 400 INVALID_PRIORITY). This used to key off a top-level
            # ``error`` field that the API does not send, so every priority
            # refusal fell through to the generic ServerException below and
            # told the customer the service team had been notified -- for a
            # 4xx that is theirs to fix and that the API exists to return.
            priority_exception = Werk24Client._priority_exception(response)
            if priority_exception is not None:
                logger.warning("Priority error received: %s", error_message)
                raise priority_exception from exception

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
            session = self._https_session()
            # The response is context-managed. With a per-call session the
            # session's own close released it; with a pooled one an
            # unreleased response holds its connector slot until the garbage
            # collector gets to it, which is the pooling this change is for.
            # _s3_error_detail returns immediately for a 2xx without touching
            # the body, so nothing else would release it.
            async with session.post(str(presigned_post.url), data=form) as response:
                self._raise_for_status(
                    str(presigned_post.url),
                    response.status,
                    details=await self._s3_error_detail(response),
                )
            logger.info("File uploaded successfully.")
        except aiohttp.ClientConnectorCertificateError as exc:
            raise SSLCertificateError("SSL certificate error occurred.") from exc
        except Exception as exc:
            logger.error("File upload failed: %s", exc)
            raise

    @staticmethod
    async def _s3_error_detail(response: Any) -> Optional[str]:
        """The reason S3 gives for refusing an upload, or ``None``.

        A refused presigned POST answers with an XML body naming the
        condition that failed -- ``EntityTooLarge`` when the drawing is over
        the policy's size range, ``EntityTooSmall`` when it is empty,
        ``MalformedPOSTRequest`` when the form is not shaped the way S3
        wants, ``InvalidArgument`` when a field is missing or repeated.
        Without it a caller is told only that "the server could not
        interpret the request", which is the same sentence for all of them
        and points at the wrong end of the problem: none of those is a bad
        request in the sense the message suggests, and the most common one
        is a file the account is not allowed to send at that size.

        Best effort by construction. It runs on a path that is already
        failing, so anything that goes wrong reading the body -- a
        connection that dropped, a body that is not XML, an S3 response
        shape that changes -- leaves the caller with the status-code
        message it had before rather than replacing one failure with
        another.
        """
        if 200 <= response.status < 300:
            return None

        try:
            # Off the stream, not through ``text()``: that buffers the whole
            # body before anything can trim it, so the limit below would
            # bound only what is searched and not what is read. The endpoint
            # answering here is not always S3 itself -- a proxy or an
            # S3-compatible gateway can sit in front of it -- and a 4xx body
            # that is large or never ends would then be allocated in full, or
            # waited on to EOF, on the path that is already failing.
            raw = await response.content.read(_S3_ERROR_BODY_LIMIT)
        except Exception:  # noqa: BLE001 - see docstring
            return None

        if not raw:
            return None

        # ``replace`` rather than a decode that can raise: a bounded read can
        # end mid-character, and a body that is not UTF-8 at all is a body
        # with no reason in it, which is the empty answer below and not an
        # error of its own.
        excerpt = raw.decode("utf-8", errors="replace")

        # Read, rather than parse: the body arrives from the network on an
        # error path, and a regex over a bounded slice cannot be talked into
        # resolving an entity or expanding a billion laughs.
        code = re.search(r"<Code>([^<]{0,200})</Code>", excerpt)
        message = re.search(r"<Message>([^<]{0,500})</Message>", excerpt)
        if code is None and message is None:
            return None

        return ": ".join(
            part.group(1).strip()
            for part in (code, message)
            if part is not None and part.group(1).strip()
        ) or None

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

    @_closes_standalone_session
    async def read_drawing_with_callback(
        self,
        drawing: Union[BufferedReader, bytes],
        asks: List[AskV2],
        callback_url: str,
        max_pages: int = 5,
        drawing_filename: Optional[str] = None,
        callback_headers: Optional[Dict[str, str]] = None,
        public_key: Optional[bytes] = None,
        priority: Optional[str] = None,
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
        - priority (Optional[str], optional): Optional priority level for the request.
            Valid values are "PRIO1", "PRIO2", "PRIO3" (case-insensitive).
            If not specified, the account's default tier is used.

        Raises:
        ------
        - BadRequestException: Raised when ask types are invalid.
        - InsufficientCreditsException: Raised when the user lacks sufficient credits
          for the request.
        - InvalidPriorityError: Raised if the priority value is invalid, either
          by this client before sending or by the API (400).
        - PriorityTooHighError: Raised when the requested priority exceeds the
          account tier (403).
        - ServerException: Raised for any other server-side failure that is not
          one of the typed exceptions above.
        - ValueError: Raised if the drawing or callback_url is invalid.

        Returns:
        -------
        - UUID4: The request ID of the registered request.
        """
        logger.debug("API method read_drawing_with_callback() called")

        # Validate ask types before sending request
        self.validate_asks(asks)

        # Validate priority before sending request
        validated_priority = validate_priority(priority)

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
            priority=validated_priority,
        )

        # create the form data
        data = aiohttp.FormData()
        data.add_field("drawing", drawing, filename=drawing_filename)
        for key, value in payload.model_dump(mode="json").items():
            data.add_field(key, json.dumps(value))

        # send the request
        headers = self._get_auth_headers()
        url = self._make_https_url("/techread/read-with-callback")
        session = self._https_session()
        # Context-managed for the same reason as the upload above: a pooled
        # session only pools if each response gives its connection back.
        async with session.post(url, data=data, headers=headers) as response:
            await self._raise_for_priority_error(response, validated_priority)
            self._raise_for_status(url, response.status)
            response_json = await response.json(content_type=None)

        try:
            return uuid.UUID(response_json["request_id"])
        except (ValueError, KeyError) as e:
            raise BadRequestException(f"Request failed: {response_json}") from e

    @staticmethod
    async def get_system_status() -> SystemStatus:
        """Fetch the current system status from the API."""

        url = urljoin(str(settings.http_server), "/status")
        ssl_context = _default_ssl_context()
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        timeout = aiohttp.ClientTimeout(total=None, sock_connect=30, sock_read=30)
        async with aiohttp.ClientSession(
            timeout=timeout, connector=connector
        ) as session:
            async with session.get(
                url, headers={"Accept": "application/json"}
            ) as response:
                Werk24Client._raise_for_status(url, response.status)
                payload = await response.json()
        return SystemStatus.model_validate(payload)

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
        self, timeout_seconds: int = 30, cafile: Optional[str] = None
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
            # Reuse the shared SSL context (built once from certifi's CA bundle)
            # unless a custom CA file is explicitly provided. Building an SSL
            # context reads/parses the CA bundle from disk, so rebuilding it on
            # every request is a needless per-request cost.
            if cafile is None:
                ssl_context = self._ssl_context
            else:
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
    def _raise_for_status(
        url: str, status_code: int, details: Optional[str] = None
    ) -> None:
        """
        Raise the correct exception based on the HTTP status code.

        Args:
        ----
        - url (str): The requested URL.
        - status_code (int): The received response status code.
        - details (Optional[str]): What the server said about the refusal,
          when the caller was able to read it. A status code alone maps a
          whole family of causes onto one sentence; this is what tells them
          apart in a log line or a support ticket.

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

        described = f"Request failed '{url}' with code {status_code}"
        if details:
            described = f"{described}: {details}"

        if exception_class:
            logger.warning(
                "Request to '%s' failed with status code %s (%s). Raising %s.",
                url,
                status_code,
                details or "no detail given",
                exception_class.__name__,
            )
            raise exception_class(described)

        # Fallback for unhandled status codes
        logger.error(
            "Request to '%s' failed with unhandled status code %s (%s).",
            url,
            status_code,
            details or "no detail given",
        )
        raise ServerException(described)

    async def _send_command_read(
        self,
        client_public_key_pem: Optional[bytes] = None,
        client_private_key_pem: Optional[bytes] = None,
        client_private_key_passphrase: Optional[bytes] = None,
        max_messages_per_session: int = 1000,
        priority: Optional[str] = None,
    ) -> AsyncGenerator[TechreadMessage, None]:
        """
        Send a techread request to the backend and yield resulting messages.

        The stream is terminated when the server sends a PROGRESS_COMPLETED
        message. ``max_messages_per_session`` is only a safety net to bound the
        loop if that signal never arrives; hitting it is logged as a warning so
        truncation is never silent.

        Args:
            client_public_key_pem (Optional[bytes]): PEM-encoded public key, if applicable.
            client_private_key_pem (Optional[bytes]): PEM-encoded private key, if applicable.
            client_private_key_passphrase (Optional[bytes]): Passphrase for the private key, if applicable.
            max_messages_per_session (int): Safety-net cap on the number of
                messages to receive per session before giving up.
            priority (Optional[str]): Optional priority level for the request (PRIO1, PRIO2, PRIO3).

        Yields:
            W24TechreadMessage: The received messages, processed as needed.
        """
        logger.debug("API method _send_command_read() called")

        # Prepare the initial request message
        message = {}
        if client_public_key_pem:
            message["public_key"] = client_public_key_pem.decode("utf-8")
            logger.debug("Public key added to message")

        # Include priority in message if specified (ensure uppercase)
        if priority:
            message["priority"] = priority.upper()
            logger.debug("Priority added to message: %s", priority.upper())

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
        completed = False
        hit_cap = True
        # (message, download task or None), in receive order.
        pending: deque = deque()
        try:
            for _ in range(max_messages_per_session):
                try:
                    raw_message = str(await self._wss_session.recv())
                except websockets.exceptions.ConnectionClosedOK:
                    # Server closed the stream cleanly.
                    hit_cap = False
                    break
                except websockets.exceptions.ConnectionClosedError as exc:
                    # Abnormal close mid-stream: the read was interrupted and the
                    # results are likely incomplete. Surface this instead of
                    # silently treating it as a normal end-of-stream.
                    raise ServerException(
                        details=(
                            "The connection to the server was closed "
                            f"unexpectedly while reading results: {exc}"
                        )
                    ) from exc

                message = self._parse_message(raw_message)
                logger.info(
                    "Received message type: %s, subtype: %s",
                    message.message_type,
                    message.message_subtype,
                )

                # Start the payload download, but do not wait for it here.
                #
                # Downloading inline blocked receipt of the next ASK message
                # for the whole transfer, so a three-ask read paid three
                # downloads strictly in series with the messages that carry
                # them. The server sends each ASK as its result becomes ready,
                # usually seconds apart, so a download started now has almost
                # always finished before the next message arrives.
                #
                # Messages are still yielded in order and still carry their
                # ``payload_bytes`` when they are yielded: only the waiting
                # moves. ``pending`` holds at most one message back, which is
                # what creates the overlap.
                if message.payload_url:
                    logger.debug(
                        "Downloading payload from URL: %s", message.payload_url
                    )
                    task = asyncio.ensure_future(
                        self.download_payload(
                            message.payload_url,
                            client_private_key_pem,
                            client_private_key_passphrase,
                        )
                    )
                else:
                    task = None
                pending.append((message, task))

                is_completed = (
                    message.message_type == TechreadMessageType.PROGRESS
                    and message.message_subtype
                    == TechreadMessageSubtype.PROGRESS_COMPLETED
                )

                # Keep one message in flight so its download overlaps the next
                # receive; on completion there is no next receive, so drain.
                while len(pending) > (0 if is_completed else 1):
                    ready, ready_task = pending.popleft()
                    if ready_task is not None:
                        try:
                            ready.payload_bytes = await ready_task
                            logger.debug("Payload successfully downloaded")
                        except Exception as e:
                            logger.error("Failed to download payload: %s", e)
                            raise
                    yield ready

                # Stop once the server signals that the read has completed,
                # rather than relying on a fixed message count (which would
                # silently truncate large results).
                if is_completed:
                    completed = True
                    hit_cap = False
                    break

            # Every way out of that loop except an exception is a NORMAL end,
            # and the message held back to create the overlap is a real
            # message. A clean server close (ConnectionClosedOK) and the
            # message cap both land here with one still queued; dropping it
            # would lose an answer the customer was sent, and at a cap of 1
            # would yield nothing at all.
            #
            # After a PROGRESS_COMPLETED break this is empty - that path
            # already drained - so it costs nothing there.
            while pending:
                ready, ready_task = pending.popleft()
                if ready_task is not None:
                    try:
                        ready.payload_bytes = await ready_task
                        logger.debug("Payload successfully downloaded")
                    except Exception as e:
                        logger.error("Failed to download payload: %s", e)
                        raise
                yield ready

        except Exception as e:
            logger.error("Error occurred while processing responses: %s", e)
            raise
        finally:
            # Only an abnormal end reaches here with anything queued: the loop
            # raised, or the caller stopped consuming. Those downloads must
            # not keep running against a session that is about to close.
            #
            # Cancel, then await. A task that already FAILED is done, so
            # cancelling it is a no-op and its exception would never be
            # retrieved - asyncio then prints "Task exception was never
            # retrieved" and the real download error is lost behind it.
            # gather(return_exceptions=True) collects both cases and raises
            # neither, which is what a cleanup path should do.
            orphans = [task for _, task in pending if task is not None]
            pending.clear()
            for orphan in orphans:
                if not orphan.done():
                    orphan.cancel()
            if orphans:
                await asyncio.gather(*orphans, return_exceptions=True)

        # Warn (never silently truncate) if the stream ended without an explicit
        # completion signal.
        if hit_cap:
            logger.warning(
                "Reached max_messages_per_session=%d without a PROGRESS_COMPLETED "
                "message; results may be truncated.",
                max_messages_per_session,
            )
        elif not completed:
            logger.warning(
                "Result stream ended before a PROGRESS_COMPLETED message was "
                "received; results may be incomplete."
            )

    @staticmethod
    def _validate_payload_url(payload_url: Union[HttpUrl, str]) -> None:
        """
        Validate a server-supplied payload URL before downloading from it.

        The payload URL is taken from the (untrusted) WebSocket message stream.
        A malicious or compromised server, or an injected message, could point it
        at an internal address (e.g. a cloud metadata endpoint) or a non-HTTPS
        scheme. To prevent server-side request forgery and payload injection we
        require the URL to be HTTPS and reject hosts that are private, loopback,
        link-local, reserved, or multicast IP literals.

        Raises:
        ------
        - RuntimeError: If the URL does not use HTTPS, has no host, or points at
          a non-public IP address.
        """
        parsed = urlparse(str(payload_url))

        if parsed.scheme != "https":
            raise RuntimeError(
                f"Refusing to download payload from non-HTTPS URL: {payload_url}"
            )

        host = parsed.hostname
        if not host:
            raise RuntimeError(
                f"Refusing to download payload from URL without a host: {payload_url}"
            )

        # If the host is an IP literal, block non-public ranges. Hostnames are
        # left to DNS/TLS; blocking IP literals stops the most direct SSRF
        # vectors (e.g. https://169.254.169.254/...).
        try:
            ip = ipaddress.ip_address(host)
        except ValueError:
            ip = None
        if ip is not None and (
            ip.is_private
            or ip.is_loopback
            or ip.is_link_local
            or ip.is_reserved
            or ip.is_multicast
            or ip.is_unspecified
        ):
            raise RuntimeError(
                f"Refusing to download payload from non-public address: {payload_url}"
            )

    @_closes_standalone_session
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

        # Validate the (untrusted) URL before issuing any request.
        self._validate_payload_url(payload_url)

        # Attempt to download the payload
        try:
            session = self._https_session()
            logger.debug("Sending GET request to %s", payload_url)
            async with session.get(str(payload_url)) as response:
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
