import asyncio
from typing import List

from werk24 import Hook, W24TechreadClient


async def w24_read_async(
    document_bytes: bytes,
    hooks:  List[Hook],
    max_pages: int = 5
) -> None:
    """ Convenient handler to submit an asynchronous request to the
    Werk24 TechRead API.

    Args:
        document_bytes (bytes): Document bytes
        hooks (List[Hook]): List of Hooks that you want to
            submit.
    """
    async with W24TechreadClient.make_from_env() as session:
        await session.read_drawing_with_hooks(document_bytes, hooks, max_pages)


def w24_read_sync(
    document_bytes: bytes,
    hooks:  List[Hook],
    max_pages: int = 5
) -> None:
    """ Convenient handler to submit a synchronous request to the
    Werk24 TechRead API.

    Args:
        document_bytes (bytes): Document bytes
        hooks (List[Hook]): List of Hooks that you want to
            submit.
    """
    asyncio.run(w24_read_async(document_bytes, hooks, max_pages))
