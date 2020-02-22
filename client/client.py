""" W24Client Module

The module contains everything that is needed to
communicate with the W24 API - allowing you
to interpret the contents of your technical drawings.
"""

import json
from typing import Callable, List, Tuple, Union

import websockets
import logging

from models.architecture import W24Architecture
from models.ask import W24Ask
from models.ask_measures import W24AskMeasures
from models.ask_thumbnail import W24AskThumbnail
from models.ask_thumbnail_canvas import W24AskThumbnailCanvas
from models.ask_thumbnail_page import W24AskThumbnailPage
from models.ask_thumbnail_sheet import W24AskThumbnailSheet
from models.attachment_drawing import W24AttachmentDrawing
from models.attachment_model import W24AttachmentModel
from models.drawing_read_message import W24DrawingReadMessage
from models.drawing_read_request import W24DrawingReadRequest
from models.drawing_read_response import W24DrawingReadResponse

from .cognito_client import CognitoClient


# make the logger
logger = logging.getLogger('w24client')


class UnauthorizedException(Exception):
    """ Exception that is raised when the
    response code is 403 - Unauthorized
    """


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
            return await func(self, *args, **kwargs)

        # if we obtain a UnauthorizedException, we
        # have the chance that the toke painly expired.
        # So let's try again
        except UnauthorizedException:
            logger.warn("API call failed with UnauthorizedException.")
            await self.auth_service.login()
            return await func(self, *args, **kwargs)

    return decorator


class W24Client():
    """ Simple W24Client that allows you to use
    learn more about the content on your Technical
    Drawings.
    """

    def __init__(
            self,
            w24_server: str,
            w24_version: str = "v1"):

        # Create an empty reference to the authentication
        # service (currently AWS Cognito)
        self.auth_service = None

        # store the w24 info locally
        self._w24_server = w24_server
        self._w24_version = w24_version

    def register(
            self,
            cognito_region: str,
            cognito_identity_pool_id: str,
            cognito_client_id: str,
            cognito_client_secret: str,
            username: str,
            password: str) -> None:
        """ Register with the authentication
        service

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
    async def ping(self) -> str:
        """ Send a ping to the W24 API and
        expect "pong" as response. This is
        plainly to test the connection (speed).

        Returns:
            str -- "pong"
        """
        logger.info("API method ping() called")

        # send the ping to the websocket
        async with self._w24_session as websocket:

            # send the drawing read request
            await websocket.send(W24DrawingReadMessage(action="ping", message="ping").json())

            # wait for the responses and interpret
            response = json.loads(await websocket.recv())

        return response

    @ensure_authentication
    async def read_drawing(
            self,
            drawing: bytes,
            model: bytes = None,
            ask_thumbnail_page: Tuple[int, int, bool] = None,
            ask_thumbnail_sheet: Tuple[int, int, bool] = None,
            ask_thumbnail_canvas: Tuple[int, int, bool] = None,
            ask_measures: bool = False,
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

            ask_thumbnail_page {Tuple[int, int, bool]} --
                Tuple of max_width, max_height, auto_rotate indicating that
                you wish to obtain a thumbnail of the page(default: {None})

            ask_thumbnail_sheet {Tuple[int, int, bool]} --
                Tuple of max_width, max_height, auto_rotate indicating that
                you wish to obtain a thumbnail of the sheet(default: {None})

            ask_thumbnail_canvas {Tuple[int, int, bool]} --
                Tuple of max_width, max_height, auto_rotate indicating that
                you wish to obtain a thumbnail of the canvas(default: {None})

            ask_measures {bool} -- Ask to the Measures depicted
                on the technical drawing(default: {False})

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
        print("test")

        # make the asks
        asks = self._make_asks(
            ask_thumbnail_page,
            ask_thumbnail_sheet,
            ask_thumbnail_canvas,
            ask_measures)

        # make the drawing attachment
        drawing_attachment = self._make_attachment(
            W24AttachmentDrawing, drawing)

        # make the model attachment
        model_attachment = self._make_attachment(
            W24AttachmentModel, model)

        # make the request
        request = W24DrawingReadRequest(
            drawing=drawing_attachment,
            model=model_attachment,
            asks=asks,
            architecture=architecture)

        # connect
        async with self._w24_session as websocket:

            # send the drawing read request
            response = await websocket.send(
                W24DrawingReadMessage(
                    action="read_drawing",
                    message=request.json()).json())
            logger.info(f"Response: {response}")

            # wait for the responses and interpret
            while True:
                response = await websocket.recv()
                logger.info(f"Response: {response}")

    @property
    def _w24_session(self) -> websockets.server:
        """Get a reference to the W24 Session
        including the correct headers

        TODO: store local reference
        """
        endpoint = f"wss://{self._w24_server}/{self._w24_version}"
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

        return f"{protocol}://{self._w24_server}/{path}"

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

    @classmethod
    def _make_asks(
            cls,
            ask_thumbnail_page,
            ask_thumbnail_sheet,
            ask_thumbnail_canvas,
            ask_measures) -> List[W24Ask]:
        """ Turn the arguments (easier for the sdk-user)
        into a list of asks that can be passed to the
        backend.

        Arguments:
            ask_thumbnail_page {Tuple[int, int, bool]} --
                Tuple of max_width, max_height, auto_rotate indicating that
                you wish to obtain a thumbnail of the page(default: {None})

            ask_thumbnail_sheet {Tuple[int, int, bool]} --
                Tuple of max_width, max_height, auto_rotate indicating that
                you wish to obtain a thumbnail of the sheet(default: {None})

            ask_thumbnail_canvas {Tuple[int, int, bool]} --
                Tuple of max_width, max_height, auto_rotate indicating that
                you wish to obtain a thumbnail of the canvas(default: {None})

            ask_measures {bool} -- Ask to the Measures depicted
                on the technical drawing(default: {False})

        Returns:
            List[W24Ask] -- A list with all the asks from the API
        """

        # start with an empty list
        asks = []

        # add the thumbnail page
        if ask_thumbnail_page is not None:
            asks.append(cls._make_w24_request_ask_thumbnail(
                W24AskThumbnailPage,
                ask_thumbnail_page))

        # add the thumbnail sheet
        if ask_thumbnail_sheet is not None:
            asks.append(cls._make_w24_request_ask_thumbnail(
                W24AskThumbnailSheet,
                ask_thumbnail_sheet))

        # add the thumbnail canvas
        if ask_thumbnail_canvas is not None:
            asks.append(cls._make_w24_request_ask_thumbnail(
                W24AskThumbnailCanvas,
                ask_thumbnail_canvas))

        # add the measures
        if ask_measures:
            asks.append(W24AskMeasures())

        return asks

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
