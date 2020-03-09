""" W24Client Module

DESCRIPTION
    The module contains everything that is needed to
    communicate with the W24 API - allowing you
    to interpret the contents of your technical drawings.

AUTHOR
    Jochen Mattes (Werk24)

STYLEGUIDE
    pylint

EXAMPLE
    # obtain the thumbnail of a page
    import logging
    drawing_bytes = open(...,"r").read()
    client = W24TechreadClient.make_from_dotenv()
    await client.read_drawing_with_callback_requests(
        drawing_bytes,
        [CallbackRequest(
                ask=W24ASkThumbnailPage(),
                callback=lambda msg: logging.info("Received Thumbnail of Page")]))
"""
import asyncio
import logging
from typing import Callable, Dict, List, Optional

from pydantic import BaseModel

from werk24.models.ask import W24Ask, W24AskType
from werk24.models.techread import W24TechreadMessageType, W24TechreadRequest, W24TechreadArchitecture, W24TechreadArchitectureStatus

from .auth_client import AuthClient
from .techread_client_https import TechreadClientHttps
from .techread_client_wss import TechreadClientWss

# make the logger
logger = logging.getLogger('w24_techread_client')


class CallbackRequest(BaseModel):
    """ Small Object to keep the callback requests.
    You can either register a callback request to an
    ask or a message_type.

    If you register an ask, be sure to use a complete W24Ask
    definition; not just the ask type.
    """
    ask: Optional[W24Ask] = None
    message_type: Optional[W24TechreadMessageType] = None
    callback: Callable


class W24TechreadClient():
    """ Simple W24Client that allows you to use
    learn more about the content on your Technical
    Drawings.
    """

    message_to_ask_type: Dict[W24TechreadMessageType, W24AskType] = {
        W24TechreadMessageType.ASK_THUMBNAIL_DRAWING: W24AskType.THUMBNAIL_DRAWING,
        W24TechreadMessageType.ASK_THUMBNAIL_PAGE: W24AskType.THUMBNAIL_PAGE,
        W24TechreadMessageType.ASK_THUMBNAIL_SHEET: W24AskType.THUMBNAIL_SHEET,
        W24TechreadMessageType.ASK_PART_OVERALL_DIMENSIONS: W24AskType.PART_OVERALL_DIMENSIONS
    }

    def __init__(
            self,
            techread_server_https: str,
            techread_server_wss: str,
            techread_version: str):
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
        """

        # Create an empty reference to the authentication
        # service (currently AWS Cognito)
        self._auth_client = None

        # Initialize an instance of the HTTPS client
        self._techread_client_https = TechreadClientHttps(
            techread_server_https,
            techread_version)

        # Initialize an instance of the WEBSCOKET client
        self._techread_client_wss = TechreadClientWss(
            techread_server_wss,
            techread_version)

    async def __aenter__(self):
        """ Create the HTTPS and WSS sessions

        Raises:
            RuntimeError: Exception is raised if
                you tried to enter a session before
                calling the register() method

        Returns:
            W24TechreadClient -- Version of self with
                active sessions
        """

        # ensure that register() was called
        if self._auth_client is None:
            raise RuntimeError(
                "No connection to the authentication service was "
                + "established. Please call register()")

        # ensure that we have a token
        if self._auth_client.token is None:
            await self._auth_client.login()

        # enter the https session
        await self._techread_client_https.__aenter__()

        # enter the wss session
        await self._techread_client_wss.__aenter__()

        # return the "entered" version of self
        return self

    async def __aexit__(self, exc_type, exc, traceback):
        """ Ensure that the sessions are closed
        """

        # close the HTTPS session
        await self._techread_client_https.__aexit__(exc_type, exc, traceback)

        # close the WSS session
        await self._techread_client_wss.__aexit__(exc_type, exc, traceback)

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
        self._auth_client = AuthClient(
            cognito_region,
            cognito_identity_pool_id,
            cognito_client_id,
            cognito_client_secret)

        # register username and password
        self._auth_client.register(username, password)

        # tell the techread clients about it
        self._techread_client_https.register_auth_client(self._auth_client)
        self._techread_client_wss.register_auth_client(self._auth_client)

    async def get_architecture_status(self, architecture: W24TechreadArchitecture) -> W24TechreadArchitectureStatus:
        """ Talk to the API endpoint and check whether a specific architecture
        is currently available. This only relevant if you have booked a
        dedicated GPU infrastructure that.

        Arguments:
            architecture {W24TechreadArchitecture} -- Architecture in question

        Returns:
            W24TechreadArchitectureStatus -- Status

        """
        return await self._techread_client_https.get_architecture_status(architecture)

    async def read_drawing(
            self,
            drawing: bytes,
            asks: List[W24Ask],
            model: bytes = None,
            architecture=W24TechreadArchitecture.GPU_V1):
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
                list of supported architectures (default: {W24TechreadArchitecture.GPU_V1})

        Returns:
            W24DrawingReadResponse -- Response object obtained from the API
                that indicates the state of your request. Be sure to pass this
                to the read_drawing_listen method
        """

        # give us some debug information
        logger.info("API method read_drawing() called")

        # make the request
        request = W24TechreadRequest(
            asks=asks,
            architecture=architecture)

        # send the initialization request to the server.
        # This achieves two things:
        # 1. The server has a couple of 100ms to
        #    reserves some resources for you, and
        # 2. The server will create a new request_id
        #    that you will need when uploading the
        #    associated files
        await self._techread_client_wss.send_command("initialize", request.json())

        # Wait for the response (i.e,. the request id)
        response = await self._techread_client_wss.recv_message()
        logger.info("Received request_id %s", response.request_id)

        # upload drawing and model. We can do that in parallel.
        # If your user uploads them separately, you could also
        # upload them separately to Werk24.
        await asyncio.gather(*[
            self._techread_client_https.upload_associated_file(
                response.request_id, 'drawing', drawing),
            self._techread_client_https.upload_associated_file(
                response.request_id, 'model', model)])
        logger.info("Drawing(and model) uploaded")

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
        await self._techread_client_wss.send_command("read", "{}")
        logger.info("Reading process started")

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
                message.payload_bytes = await self._techread_client_https.download_payload(
                    message.payload_url)

            # return the message to the caller for immediate
            # consumption
            yield message

    @staticmethod
    def make_from_dotenv() -> "W24TechreadClient":
        """ Small helper function that creates a new
        W24TechreadClient from the enviorment info.

        If use_dotenv is set to True, we load the
        data from the .env file (that you will be provided
        with off-band). This is the standard way
        of creating a client instance.


        Keyword Arguments:
            use_dotenv {bool} -- if set to True, we
                load the environment variables from
                the .env file (default: {True})

        Returns:
            W24TechreadClient -- [description]
        """
        import os
        from dotenv import load_dotenv

        # load the dotenv file into the os environment
        load_dotenv()

        # create a reference to the client
        client = W24TechreadClient(
            os.environ.get("W24TECHREAD_SERVER_HTTPS"),
            os.environ.get("W24TECHREAD_SERVER_WSS"),
            os.environ.get("W24TECHREAD_VERSION"))

        # login with the credentials
        client.login(
            os.environ.get("W24TECHREAD_AUTH_REGION"),
            os.environ.get("W24TECHREAD_AUTH_IDENTITY_POOL_ID"),
            os.environ.get("W24TECHREAD_AUTH_CLIENT_ID"),
            os.environ.get("W24TECHREAD_AUTH_CLIENT_SECRET"),
            os.environ.get("W24TECHREAD_AUTH_USERNAME"),
            os.environ.get("W24TECHREAD_AUTH_PASSWORD"))

        # return the client
        return client

    async def read_drawing_with_callback_requests(
            self,
            drawing_bytes: bytes,
            callback_requests: List[CallbackRequest]):
        """ Send the drawing to the API (can be PDF or image)
        and register a number of callbacks that are triggered
        once the asks become available.

        Arguments:
            drawing_bytes {bytes} -- Technical Drawing as Image or PDF
            callback_requests {List[CallbackRequest]} -- List of Callback you want to obtain
        """

        # Create a new client session with the server.
        # Each techread request requires its own session
        async with self as session:

            # filter the callback requests to only contain
            # the ask types
            asks_list = [
                cur_ask.ask
                for cur_ask in callback_requests
                if cur_ask.ask is not None]

            # send out the request and make a generator
            # that triggers when the result of an ask
            # becomes available
            async for message in session.read_drawing(drawing_bytes, asks_list):

                # if the message type starts with TECHREAD_, it
                # corresponds to a process message, so check the
                # process handlers
                if message.message_type.startswith("TECHREAD_"):

                    # check whether the message_type is associated
                    # with a callback. If not, the message type
                    # is simply ignored
                    try:
                        callback = [
                            cb
                            for cb in callback_requests
                            if cb.message_type == message.message_type][0].callback

                    # if there is no associated callback request,
                    # silently ignore
                    except IndexError:
                        continue

                # if the message tyep starts with ASK_, it corresponds
                # to a ASK, so check the asks_dict
                elif message.message_type.startswith("ASK_"):
                    # translate the message_type into a ask_type
                    cur_ask_type = self.message_to_ask_type.get(
                        message.message_type)

                    # obtain the trigger that is associated to the ask type
                    try:
                        callback = [
                            cb
                            for cb in callback_requests
                            if cb.ask is not None and cb.ask.ask_type == cur_ask_type][0].callback

                    # if the ask is not in the list, the API returned something
                    # that the client was not asking for.
                    except IndexError:
                        logger.warning(
                            "No callback associated with ask type '%s'. The original message_type was '%s'. If you did not request this ask type, please get in touch with our support team",
                            cur_ask_type,
                            message.message_type)
                        continue

                # if neither is true, we have an unknown message type, which
                # probobly is being caused by an API update. We want to ensure
                # that the user is being informed, but we do not want to break
                # the existing functionality -> warning
                else:
                    logger.warning(
                        "Ignoring unknown message type %s. Please check with our support team",
                        message.message_type)

                # if the callback is not callable, we want to warn the user,
                # rather than throwing an exception
                if not callable(callback):
                    logger.warning(
                        "You registered a non-callable trigger of type '%s' with the message_type '%s'. Please make sure that you are using a Callable (e.g, def or lambda)",
                        type(callback),
                        message.message_typ)
                    continue

                # if everything went well, we call the trigger with
                # the message as payload. Be sure to call the
                # function asymmetrically if supported
                if asyncio.iscoroutinefunction(callback):
                    await callback(message)
                else:
                    callback(message)
