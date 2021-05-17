""" Websocket-part of the Werk24 client
"""
import json
from types import TracebackType
from typing import Optional, Type, AsyncGenerator

import websockets
from pydantic import ValidationError
from websockets.client import WebSocketClientProtocol
from werk24.exceptions import ServerException, UnauthorizedException
from werk24.models.techread import W24TechreadCommand, W24TechreadMessage

from .auth_client import AuthClient


class TechreadClientWss:
    """ TechreadClient subpart that handles the websocket
    communication with the server.
    """

    def __init__(self, techread_server_wss: str, techread_version: str):
        self._auth_client: Optional[AuthClient] = None
        self._techread_server_wss = techread_server_wss
        self._techread_version = techread_version
        self._techread_session_wss: Optional[WebSocketClientProtocol] = None

    async def __aenter__(
            self
    ) -> 'TechreadClientWss':
        """ Enter the session with the wss server

        Raises:
            RuntimeError  -- Raise when the developer enters the session
                without having called register_auth_client()

        Returns:
            TechreadClientWss -- instance with activated session
        """

        # make sure that we have an AuthClient
        if self._auth_client is None:
            raise RuntimeError(
                "You need to call register_auth_client() before you can start"
                + " the session")

        # make the endpoint
        endpoint = "wss://{}/{}".format(
            self._techread_server_wss,
            self._techread_version)

        # make the ehaders
        headers = [("Authorization", f"Bearer {self._auth_client.token}")]

        # now make the session
        self._techread_session_wss = await websockets.connect(
            endpoint,
            extra_headers=headers)

        # return ourselfves
        return self

    async def __aexit__(
            self,
            exc_type: Optional[Type[BaseException]],
            exc_value: Optional[BaseException],
            traceback: Optional[TracebackType]
    ) -> None:

        """ Close the session
        """
        if self._techread_session_wss is not None:
            await self._techread_session_wss.close()

    def register_auth_client(self, auth_client: AuthClient) -> None:
        """Register the reference to the authentication service

        Arguments:
            auth_client {AuthClient} -- Reference to Authentication
                client
        """
        self._auth_client = auth_client

    async def send_command(
            self,
            action: str,
            message: str = "{}"
    ) -> None:
        """ Send a command to the websocket.

        The function wrapps your action and message into
        a W24TechreadCommand object, translates it to
        json and sends it to the server.

        Be sure to collect the server response from the
        socket using recv_message()

        Arguments:
            action {str} -- Action that is requested
            message {str} -- Auxilliary data that you wnat to send along
                with the message. To keep it easily expandable, we use
                a json encoded string.

        Raises:
            RuntimeError  -- Raise when the developer tries to send a command
                without entering the profile
        """

        # make sure that we have an AuthClient
        if self._techread_session_wss is None:
            raise RuntimeError(
                "You need to call enter the profile before sending a command")

        # make the command
        command = W24TechreadCommand(action=action, message=message)

        # send the the command
        await self._techread_session_wss.send(command.json())

    async def recv_message(self) -> W24TechreadMessage:
        """ Receive a message from the websocket and interpret
        the result as W24TechreadMessage

        Raises:
            RuntimeError  -- Raise when the developer tries to send a command
                without entering the profile

        Returns:
            W24TechreadMessage -- interpreted message
        """

        # make sure that we have an AuthClient
        if self._techread_session_wss is None:
            raise RuntimeError(
                "You need to call enter the profile before receiving command")

        # wait for the websocket to say something
        message_raw = str(await self._techread_session_wss.recv())

        # process the message
        message = await self._process_message(message_raw)

        # and finally return
        return message

    @staticmethod
    async def _process_message(message_raw: str) -> W24TechreadMessage:
        """ Interpret the raw websocket message and
        turn it inot a W24TechreadMessage

        Arguments:
            message_raw {str} -- Raw message

        Raises:
            UnauthorizedException: Exception is raised
                when you requested an action that you
                have no priviledges for (or that does
                not exist)

            ServerException: Exception is raised when
                the server did not respond as expected

        Returns:
            W24TeachreadMessage -- interpreted message
        """

        # interpret and return
        try:
            message = W24TechreadMessage.parse_raw(message_raw)

        # if that failes, we are probably receiving a
        # message from the gateway directly
        except ValidationError:

            # The Gateway responds with the format
            # {"message": str, "connectionId":str, "requestId":str}
            # Obtain the message
            response = json.loads(message_raw)
            message = response.get('message')

            # raise a specific exception if the
            # requested action was forbidden
            if message == 'Forbidden':
                raise UnauthorizedException("Requested Action forbidden")

            # otherwise fail with an UnknownException
            raise ServerException(
                f"Unexpected server response '{message_raw}'.")

        return message

    async def listen(self) -> AsyncGenerator[W24TechreadMessage, None]:
        """ Simple generator that waits for
        messages on the websocket, interprets
        them and yields them

        Yields:
            W24TechreadMessage -- interpreted message from the socket

        Raises:
            RuntimeError  -- Raise when the developer tries to send a command
                without entering the profile
        """

        # make sure that we have an AuthClient
        if self._techread_session_wss is None:
            raise RuntimeError(
                "You need to call enter the profile before listening")

        # wait for incoming messages
        async for message_raw in self._techread_session_wss:

            # process the message and return them to the caller
            yield await self._process_message(str(message_raw))
