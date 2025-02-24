import asyncio
from collections import defaultdict
from importlib.resources import files
from io import BufferedReader, BytesIO
from typing import Union

from werk24.models import AskUnion, TechreadMessage, TechreadMessageType

FILE_PATH = files("werk24") / "assets/DRAWING_SUCCESS.png"


def get_test_drawing():
    return open(FILE_PATH, "rb")


def read_drawing_sync(
    drawing: Union[BufferedReader, bytes, BytesIO], asks: list[AskUnion]
) -> list[TechreadMessage]:
    """
    Reads a drawing and returns the messages from the server.

    Args:
    ----
    - drawing (Union[BufferedReader, bytes, BytesIO]): The drawing to read.
    - asks (list[AskUnion]): The requests to make to the server.
    """
    from werk24.techread import Werk24Client  # import here to avoid circular imports

    async def run():
        async with Werk24Client() as client:
            return [
                msg.payload_dict
                async for msg in client.read_drawing(drawing, asks)
                if msg.message_type == TechreadMessageType.ASK
            ]

    return asyncio.run(run())


def read_example_drawing(asks: list[AskUnion]):
    drawing = get_test_drawing()
    responses = read_drawing_sync(drawing, asks)

    results = defaultdict(list)
    for msg in responses:
        if msg.message_type == TechreadMessageType.ASK:
            results[msg.message_subtype].append(msg)

    return results
