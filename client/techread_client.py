""" W24Client Module

The module contains everything that is needed to
communicate with the W24 API - allowing you
to interpret the contents of your technical drawings.
"""
import asyncio
import logging
from typing import List

from models.architecture import W24Architecture
from models.ask import W24Ask
from models.techread import W24TechreadRequest

from .auth_client import AuthClient
from .techread_client_https import TechreadClientHttps
from .techread_client_wss import TechreadClientWss

# make the logger
logger = logging.getLogger('w24client')


class W24TechreadClient():
    """ Simple W24Client that allows you to use
    learn more about the content on your Technical
    Drawings.
    """

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

    async def __aexit__(self, exc_type, exc, tb):
        """ Ensure that the sessions are closed
        """

        # close the HTTPS session
        await self._techread_client_https.__aexit__(exc_type, exc, tb)

        # close the WSS session
        await self._techread_client_wss.__aexit__(exc_type, exc, tb)

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
            self._techread_client_https.upload_associated_file(response.request_id, 'drawing', drawing),
            self._techread_client_https.upload_associated_file(response.request_id, 'model', model)])
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
