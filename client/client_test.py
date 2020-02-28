import asyncio
import logging
import os

from dotenv import load_dotenv

from .client import W24Client, logger, W24AskMeasures

# load the environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)


def _get_test_drawing() -> bytes:
    """ Obtain the bytes content of the test drawing
    """
    cwd = os.path.dirname(os.path.abspath(__file__))
    test_file_path = os.path.join(cwd, "client_test_drawing.png")

    with open(test_file_path, "rb") as filehandle:
        content_bytes = filehandle.read()

    return content_bytes


# make the client reference
client = W24Client(
    os.environ.get("W24IO_SERVER_HTTPS"),
    os.environ.get("W24IO_SERVER_WSS"),
    os.environ.get("W24IO_VERSION"))
client.login(
    os.environ.get("W24IO_COGNITO_REGION"),
    os.environ.get("W24IO_COGNITO_IDENTITY_POOL_ID"),
    os.environ.get("W24IO_COGNITO_CLIENT_ID"),
    os.environ.get("W24IO_COGNITO_CLIENT_SECRET"),
    os.environ.get("W24IO_COGNITO_USERNAME"),
    os.environ.get("W24IO_COGNITO_PASSWORD"))


async def test_read_drawing(drawing_bytes):

    # send out the request and make a generator
    # that triggers when the result of an ask
    # becomes available
    generator = await client.read_drawing(
        [W24AskMeasures()],
        drawing_bytes)

    # wait for the asks
    async for res in generator:
        print(res)


if __name__ == "__main__":
    asyncio.run(test_read_drawing(_get_test_drawing()))
