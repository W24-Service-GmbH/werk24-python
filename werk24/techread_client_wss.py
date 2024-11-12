""" Websocket-part of the Werk24 client
"""
import json
from packaging.version import Version
from types import TracebackType
from typing import Optional, Type, AsyncGenerator

import websockets
from pydantic import ValidationError
from websockets.client import WebSocketClientProtocol
from werk24.exceptions import ServerException, UnauthorizedException
from werk24.models.techread import W24TechreadCommand, W24TechreadMessage
from werk24.auth_client import AuthClient
import logging

# make the logger
logger = logging.getLogger("w24_techread_client")

try:
    version = Version(websockets.__version__)
    USE_EXTRA_HEADERS = version < Version("14.0")
except:
    USE_EXTRA_HEADERS = False

class TechreadClientWss:
    """
    TechreadClient subpart that handles the websocket
    communication with the server.
    """

    def __init__(
        self, 
        techread_server_wss: str, 
        techread_version: str,
        wss_close_timeout: Optional[float] = 600
    ):
        """
        Initialize the TechreadClientWss

        Args:
        ----
        - techread_server_wss (str): The server to connect to
        - techread_version (str): The version of the server
        - wss_close_timeout (Optional[float], optional): The time to wait for the
            websocket to close. Defaults to 600.
        """
        logger.debug("Using Websockets version: %s", websockets.__version__)
        logger.debug(
            "Creating TechreadClientWss with server %s and version %s. Websocket timeout: %d",
            techread_server_wss,
            techread_version,
            wss_close_timeout
        )

        self._techread_server_wss = techread_server_wss
        self._techread_version = techread_version
        self._techread_session_wss: Optional[WebSocketClientProtocol] = None
        self.endpoint = f"wss://{self._techread_server_wss}/{self._techread_version}"
        self._auth_client = None
        self.wss_close_timeout = wss_close_timeout

    async def __aenter__(self) -> "TechreadClientWss":
        """
        Enter the session with the wss server

        Raises:
        ------
        - RuntimeError: Raise when the developer enters the session
            without having specified a token

        Returns:
        -------
        - TechreadClientWss: instance with activated session
        """
        logger.debug(f"Entered the session with the server {self._techread_server_wss}")
        headers = self._auth_client.get_auth_headers()

        if USE_EXTRA_HEADERS:
            self._techread_session_wss = await websockets.connect(
                self.endpoint,
                extra_headers=headers,
                close_timeout=self.wss_close_timeout,
            )
        else:
            self._techread_session_wss = await websockets.connect(
                self.endpoint,
                additional_headers=headers,
                close_timeout=self.wss_close_timeout,
            )
            
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        """
        Close the session
        """
        logger.debug(f"Exiting the session with the server {self._techread_server_wss}")
        if self._techread_session_wss is not None:
            await self._techread_session_wss.close()

    def register_auth_client(self, auth_client: AuthClient) -> None:
        """
        Register the reference to the authentication service

        Args:
        ----
        - auth_client (AuthClient): Reference to Authentication
            client
        """
        self._auth_client = auth_client

    async def send_command(self, action: str, message: str = "{}") -> None:
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
        if not self._techread_session_wss:
            raise RuntimeError(
                "Profile entry is required before sending commands. "
                "Please call the appropriate method to enter the profile."
            )

        # Create the command object
        command = W24TechreadCommand(action=action, message=message)
        logger.debug(f"Sending command: %s", command.model_dump_json())

        # Send the serialized command to the websocket server
        await self._techread_session_wss.send(command.model_dump_json())


    async def recv_message(self) -> W24TechreadMessage:
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
        if self._techread_session_wss is None:
            raise RuntimeError(
                "You need to call enter the profile before receiving command"
            )

        # wait for the websocket to say something and interpret the message
        message_raw = str(await self._techread_session_wss.recv())
        logger.debug(f"Received message: {message_raw}")
        message = self._parse_message(message_raw)
        return message

    @staticmethod
    def _parse_message(message_raw: str) -> W24TechreadMessage:
        """
        Interpret the raw websocket message and
        turn it into a W24TechreadMessage

        Args:
        ----
        - message_raw (str): Raw message

        Raises:
        ------
        - UnauthorizedException: Exception is raised
            when you requested an action that you
            have no privileges for (or that does
            not exist)

        - ServerException: Exception is raised when
            the server did not respond as expected

        Returns:
        -------
        - W24TeachreadMessage: interpreted message
        """
        logger.debug(f"Processing message: {message_raw}")
        try:
            return W24TechreadMessage.model_validate_json(message_raw)

        except ValidationError as exception:
            # The Gateway responds with the format
            # {"message": str, "connectionId":str, "requestId":str}
            # Obtain the message
            response = json.loads(message_raw)
            error_message = response.get("message")

            # raise a specific exception if the
            # requested action was forbidden
            if error_message == "Forbidden":
                raise UnauthorizedException("Requested Action forbidden") from exception

            # otherwise fail with an UnknownException
            raise ServerException(
                f"Unexpected server response '{message_raw}'."
            ) from exception

    async def listen(self, max_messages_per_session: int = 100) -> AsyncGenerator[W24TechreadMessage, None]:
        """
        Simple generator that waits for messages on the websocket, interprets
        them and yields them

        Yields:
        ------
        - W24TechreadMessage: interpreted message from the socket

        Raises:
        ------
        - RuntimeError: Raise when the developer tries to send a command
                without entering the profile
        """
        logger.debug("Listening for messages")

        # make sure that we have an AuthClient
        if self._techread_session_wss is None:
            raise RuntimeError("You need to call enter the profile before listening")
    
        # wait for incoming messages
        try:
            for _ in range(max_messages_per_session):
                message_raw = str(await self._techread_session_wss.recv())
                message = self._parse_message(message_raw)
                yield message
        except (
            websockets.exceptions.ConnectionClosedError, 
            websockets.exceptions.ConnectionClosedOK,
        ) as exception:
            return
