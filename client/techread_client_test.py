import asyncio
import logging
import os

from .techread_client import (W24AskMeasures, W24AskThumbnailPage,
                              W24TechreadClient, W24TechreadMessage,
                              W24TechreadMessageType, logger)

# set the log level to info for the test setting
# We recommend using logging.WARNING for production
logging.basicConfig(level=logging.INFO)


def _get_test_drawing() -> bytes:
    """ Obtain the bytes content of the test drawing
    """
    # get the path
    cwd = os.path.dirname(os.path.abspath(__file__))
    test_file_path = os.path.join(cwd, "techread_client_test_drawing.png")

    # get the content
    with open(test_file_path, "rb") as filehandle:
        return filehandle.read()


async def process_techread_message(message: W24TechreadMessage):
    """ Your custom code, that is triggered every time the
    server serves a new message
    """

    # small dictionary that maps the message types to funcitons
    TYPE = W24TechreadMessageType
    messsage_type_map = {
        TYPE.TECHREAD_STARTED: lambda msg: logging.info("Techead process started"),
        TYPE.ASK_THUMBNAIL_PAGE: lambda msg: logging.info("Received Thumbnail of Page")}

    # get the function and execute the code
    func = messsage_type_map.get(message.message_type)
    if func is not None:
        func(message)

    # if the message_type does not contain a handler for the message type,
    # raise a runtime warning
    else:
        raise RuntimeWarning(
            f"Received unhandled message of type {message.message_type}")


async def test_read_drawing(drawing_bytes: bytes):

    # make the client. This will automatically
    # fetch the authentication information
    # from the environment variables. We will
    # provide you with separate .env files for
    # the development and production environments
    client = W24TechreadClient.make_from_dotenv()

    # Create a new client session with the server.
    # Each techread request requires its own session
    async with client as session:

        # send out the request and make a generator
        # that triggers when the result of an ask
        # becomes available
        generator = session.read_drawing(
            [W24AskThumbnailPage()],
            drawing_bytes)

        # wait for the asks
        async for message in generator:
            await process_techread_message(message)


if __name__ == "__main__":

    # make the request and run
    drawing_bytes = _get_test_drawing()
    async_request = test_read_drawing(drawing_bytes)
    asyncio.run(async_request)
