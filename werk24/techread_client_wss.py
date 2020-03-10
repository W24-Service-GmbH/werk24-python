import json

import websockets
from pydantic import ValidationError

from werk24.exceptions import ServerException, UnauthorizedException
from werk24.models.techread import W24TechreadCommand, W24TechreadMessage

from .auth_client import AuthClient


class TechreadClientWss:
    def __init__(self, techread_server_wss: str, techread_version: str):
        self._auth_client = None
        self._techread_server_wss = techread_server_wss
        self._techread_version = techread_version
        self._techread_session_wss: websockets.client.WebSocketClientProtocol = None

    async def __aenter__(self):

        # make the endpoint
        endpoint = f"wss://{self._techread_server_wss}/{self._techread_version}"

        # make the ehaders
        headers = [(f"Authorization", f"Bearer {self._auth_client.token}")]

        # now make the session
        self._techread_session_wss = await websockets.connect(endpoint, extra_headers=headers)

        # return ourselfves
        return self

    async def __aexit__(self, exc_type, exc, traceback):
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

    async def send_command(self, action: str, message: str = "{}"):
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
        """
        # make the message
        message = W24TechreadCommand(action=action, message=message)

        # send the message
        await self._techread_session_wss.send(message.json())

    async def recv_message(self) -> W24TechreadMessage:
        """ Receive a message from the websocket and interpret
        the result as W24TechreadMessage

        Returns:
            W24TechreadMessage -- interpreted message
        """

        # wait for the websocket to say something
        message_raw = await self._techread_session_wss.recv()

        # process the message
        message = await self._process_message(message_raw)

        # and finally return
        return message

    async def _process_message(self, message_raw: str) -> W24TechreadMessage:
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
            raise ServerException(f"Unexpected server response '{message_raw}'.")

        return message

    async def listen(self) -> None:
        """ Simple generator that waits for
        messages on the websocket, interprets
        them and yields them

        Yields:
            W24TechreadMessage -- interpreted message from the socket
        """

        # wait for incoming messages
        async for message_raw in self._techread_session_wss:

            # process the message and return them to the caller
            yield await self._process_message(message_raw)
