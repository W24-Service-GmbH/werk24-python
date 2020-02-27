""" W24Client Module

The module contains everything that is needed to
communicate with the W24 API - allowing you
to interpret the contents of your technical drawings.
"""
import asyncio
import json
import io
import logging
from typing import Callable, List, Tuple, Union
from pydantic import ValidationError

import httpx
import websockets

from models.architecture import W24Architecture
from models.ask import W24Ask
from models.ask_measures import W24AskMeasures
from models.ask_thumbnail import W24AskThumbnail
from models.ask_thumbnail_canvas import W24AskThumbnailCanvas
from models.ask_thumbnail_page import W24AskThumbnailPage
from models.ask_thumbnail_sheet import W24AskThumbnailSheet
from models.attachment_drawing import W24AttachmentDrawing
from models.attachment_model import W24AttachmentModel
# from models.drawing_read_response import W24DrawingReadResponse
from models.techread import (W24TechreadCommand, W24TechreadMessage,
                             W24TechreadMessageType, W24TechreadRequest)

from .cognito_client import CognitoClient

# make the logger
logger = logging.getLogger('w24client')


class ClientException(Exception):
    pass


class UnauthorizedException(ClientException):
    """ Exception that is raised when
    (i) the response code is 403 - Unauthorized, or
    (ii) the requested action was forbidden by the gateway
    """


class UnknownException(ClientException):
    pass


def ensure_authentication(func: Callable) -> Callable:
    """ Decorator function that ensures that the
    called W24Client method has access to a valid
    JWT Token.

    Arguments:
        func {Callable} -- Method that is to be wrapped

    Returns:
        Callable -- Wrapped method
    """

    async def decorator(self, *args, **kwargs):

        # ensure that register() was called
        if self.auth_service is None:
            logger.error("Method call before register() was called")
            raise RuntimeError(
                "No connection to the authentication service was "
                + "established. Please call register()")

        # ensure that we have a token
        if self.auth_service.token is None:
            await self.auth_service.login()

        # call the function
        try:
            return func(self, *args, **kwargs)

        # if we obtain a UnauthorizedException, we
        # have the chance that the toke painly expired.
        # So let's try again
        except UnauthorizedException:
            logger.warn("API call failed with UnauthorizedException.")
            await self.auth_service.login()
            return func(self, *args, **kwargs)

    return decorator


class W24Client():
    """ Simple W24Client that allows you to use
    learn more about the content on your Technical
    Drawings.
    """

    def __init__(
            self,
            w24_server_https: str,
            w24_server_wss: str,
            w24_version: str):

        # Create an empty reference to the authentication
        # service (currently AWS Cognito)
        self.auth_service = None

        # store the w24 info locally
        self._w24_server_https = w24_server_https
        self._w24_server_wss = w24_server_wss
        self._w24_version = w24_version

    def login(
            self,
            cognito_region: str,
            cognito_identity_pool_id: str,
            cognito_client_id: str,
            cognito_client_secret: str,
            username: str,
            password: str) -> None:
        """
        Register with the authentication
        service (i.e., lazy login)

        Arguments:
            cognito_region {str} -- Physical region
            cognito_identity_pool_id {str} -- identity pool of W24
            cognito_client_id {str} -- the client id of your application
            cognito_client_secret {str} -- the client secrect of your application
            username {str} -- the username with which you want to register
            password {str} -- the password with which you want to register
        """
        # create an client instance to connect
        # to the authentication service
        self.auth_service = CognitoClient(
            cognito_region,
            cognito_identity_pool_id,
            cognito_client_id,
            cognito_client_secret)

        # register username and password
        self.auth_service.register(username, password)

    @ensure_authentication
    async def read_drawing(
            self,
            asks: List[W24Ask],
            drawing: bytes,
            model: bytes = None,
            architecture=W24Architecture.CPU_V1):
        """ Send a Technical Drawing to the W24 API to have it automatically
        interpreted and read. The API will return

        Arguments:
            drawing {bytes} -- binary representation of a technical drawing.
                Please refer to the API - documentation to learn which mime
                types are currently supported

        Keyword Arguments:
            model {bytes} -- binary represetation of the 3d model(typically step)
                Please refer to the API - documentation to learn whcih mime
                types are currently sypported(default: {None})

            asks {List[W24Ask]} --
                List of Asks that are requested from the API. They must derive
                from the W24Ask object. Refer to the API documentation for
                a full list of supported W24AskTypes

            architecture {str} -- Architecture to be used to process
                the request. Please refer to the API documentation for a complete
                list of supported architectures (default: {W24Architecture.CPU_V1})

        Returns:
            W24DrawingReadResponse -- Response object obtained from the API
                that indicates the state of your request. Be sure to pass this
                to the read_drawing_listen method
        """

        # give us some debug information
        logger.info("API method read_drawing() called")

        # connect to the websocket and obtain a
        # new request_id
        async with self._w24_session as websocket:

            # send the initialization request
            await self._wss_send_command(
                websocket,
                "initialize",
                W24TechreadRequest(
                    asks=asks,
                    architecture=architecture).json())
            logger.info("Request submitted")

            # wait for the response
            response = await self._wss_recv_message(websocket)
            logger.info("Received request_id %s", response.request_id)

            # upload drawing and model
            asyncio.gather(*[
                self._upload(response.request_id, 'drawing', drawing),
                self._upload(response.request_id, 'model', model)])

            # return the messages to the caller
            async for message in websocket:
                logger.info("Received message '%s'", message)
                yield message

    async def _wss_send_command(self, websocket: websockets.server, action: str, message: str) -> None:
        # make the message
        message = W24TechreadCommand(action=action, message=message)

        # send the message
        await websocket.send(message.json())

    async def _wss_recv_message(self, websocket: websockets.server) -> W24TechreadMessage:

        # wait for the websocket to say something
        response_raw = await websocket.recv()

        # interpret and return
        try:
            return W24TechreadMessage.parse_raw(response_raw)

        # if that failes, we are probably receiving a
        # message from the gateway directly
        except ValidationError:

            # The Gateway responds with the format
            # {"message": str, "connectionId":str, "requestId":str}
            # Obtain the message
            response = json.loads(response_raw)
            message = response.get('message')

            # raise a specific exception if the
            # requested action was forbidden
            if message == 'Forbidden':
                raise UnauthorizedException("Requested Action forbidden")

            # otherwise fail with an UnknownException
            raise UnknownException(
                "Unexpected server response '{response_raw}'.")

    async def _upload(self, request_id: str, filetype: str, content: bytes) -> None:
        """ Upload the associated files to the API endpoint

        Arguments:
            request_id {str} -- UUID4 request id that we obtained
                from the websocket

            filetype {str} -- filetype that we want to upload.
                currently supported: drawing, model

            content {bytes} -- content of the files

        NOTE: the complete message size must not be larger than 10 MB
        """

        # obviously stop if there is no content
        if content is None:
            return

        # make the endpoint

        endpoint = f"https://{self._w24_server_https}/{self._w24_version}/upload/{request_id}"
        async with httpx.AsyncClient() as client:
            response = await client.post(
                endpoint,
                files={filetype: io.BytesIO(content)},
                headers=[(f"Auth", f"Bearer {self.auth_service.token}")])
            print(response)

    @property
    def _w24_session(self) -> websockets.server:
        """Get a reference to the W24 Session
        including the correct headers

        TODO: store local reference
        """
        endpoint = f"wss://{self._w24_server_wss}/{self._w24_version}"
        return websockets.connect(
            endpoint,
            extra_headers=[(f"Auth", f"Bearer {self.auth_service.token}")])

    def _make_endpoint(self, path: str, protocol="https") -> str:
        """ Make the URL Endpoint of a given subpath

        Arguments:
            path {str} -- Path of the endpoint you want to call

        Keyword Arguments:
            protocol {str} -- Protocol to be used (default: https)

        Returns:
            str -- complete URL
        """

        return f"{protocol}://{self._w24_server_wss}/{path}"

    @staticmethod
    def _make_attachment(
            model: Union[W24AttachmentDrawing, W24AttachmentModel],
            attachment_bytes: bytes):
        """ Make an attachment from the supplied bytes
        """

        # return None if there is no attachment
        if attachment_bytes is None:
            return None

        # otherwise make the attachment
        return model.from_bytes(attachment_bytes)

    @staticmethod
    def _make_w24_request_ask_thumbnail(
            ask_class: W24AskThumbnail,
            ask_attrs: Tuple[int, int, bool]) -> W24AskThumbnail:
        """ Small helper function to make the AskThumbnails

        Arguments:
            ask_class {W24AskThumbnail} -- Class of the Ask
            ask_attrs {Tuple[int, int, bool]} -- Attributes

        Returns:
            W24AskThumbnail -- Instance of the Thumbnail ask
        """
        return ask_class(
            maximal_width=ask_attrs[0],
            maximal_height=ask_attrs[1],
            auto_rotate=ask_attrs[2])

    @staticmethod
    def _check_status_code(status_code: int) -> None:

        # raise an UnauthorizedException if
        # we obtain a 403
        if status_code == 403:
            raise UnauthorizedException()

        # if we obtain anything other than
        # a 200, raise a runtime error
        if status_code != 200:
            raise RuntimeError(f"Failed with status code {status_code}!")
