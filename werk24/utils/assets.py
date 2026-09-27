import asyncio
import contextvars
import threading
from collections import defaultdict
from importlib.resources import files
from io import BufferedReader, BytesIO
from typing import Any, Callable, Coroutine, TypeVar, Union

from werk24.models import AskUnion, TechreadMessage, TechreadMessageType

FILE_PATH = files("werk24") / "assets/DRAWING_SUCCESS.png"

_T = TypeVar("_T")

#: How long an interrupted synchronous call waits for the read it started to
#: cancel and close its connection before handing the interrupt back.
_CANCEL_GRACE_SECONDS = 5.0

#: Name of the helper thread that runs a read when the calling thread already
#: runs an event loop.
_HELPER_THREAD_NAME = "werk24-read-drawing-sync"


def get_test_drawing():
    return open(FILE_PATH, "rb")


def _run_blocking(make_coro: Callable[[], Coroutine[Any, Any, _T]]) -> _T:
    """Run a coroutine to completion from synchronous code.

    Without a running event loop in this thread this is ``asyncio.run()``.
    With one (a Jupyter or IPython cell, or a synchronous call made from async
    code), ``asyncio.run()`` refuses to nest, so the coroutine runs on its own
    event loop in a helper thread and this thread blocks until it finishes.

    The coroutine is created by ``make_coro`` on the thread that runs it, so
    nothing is left un-awaited if the call fails early.

    Args:
        make_coro (Callable[[], Coroutine[Any, Any, _T]]): Builds the
            coroutine to run. Called once, with no arguments.

    Returns:
        _T: What the coroutine returned.

    Raises:
        BaseException: Whatever the coroutine raised, unchanged.
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(make_coro())
    return _run_on_helper_thread(make_coro)


def _run_on_helper_thread(make_coro: Callable[[], Coroutine[Any, Any, _T]]) -> _T:
    """Run a coroutine on a new event loop in a helper thread and wait for it.

    The helper is a daemon thread, so an abandoned read never keeps the
    interpreter from exiting. The caller's context variables are copied into
    it. If the waiting thread is interrupted (``KeyboardInterrupt``, which is
    what a notebook's "interrupt kernel" raises), the read is cancelled, so
    the client leaves its ``async with`` block and closes its connections, and
    the interrupt is re-raised once that has finished or after
    ``_CANCEL_GRACE_SECONDS``.

    Args:
        make_coro (Callable[[], Coroutine[Any, Any, _T]]): Builds the
            coroutine to run. Called on the helper thread.

    Returns:
        _T: What the coroutine returned.

    Raises:
        BaseException: Whatever the coroutine raised, as the same object, so
            its type and traceback are kept.
    """
    done = threading.Event()
    cancel_requested = threading.Event()
    box: dict = {}

    async def main() -> _T:
        box["loop"] = asyncio.get_running_loop()
        box["task"] = asyncio.current_task()
        # An interrupt that arrived before the loop and task were published
        # could not cancel them, so it is honoured here instead.
        if cancel_requested.is_set():
            raise asyncio.CancelledError()
        return await make_coro()

    def target() -> None:
        try:
            box["result"] = asyncio.run(main())
        except BaseException as exc:  # handed back to the waiting thread
            box["error"] = exc
        finally:
            done.set()

    # Keep the caller's context variables visible inside the read.
    context = contextvars.copy_context()
    thread = threading.Thread(
        target=context.run,
        args=(target,),
        name=_HELPER_THREAD_NAME,
        daemon=True,
    )
    thread.start()
    try:
        # Poll rather than block without a timeout, so that a
        # KeyboardInterrupt is delivered promptly on every platform.
        while not done.wait(0.25):
            pass
    except BaseException:
        cancel_requested.set()
        loop, task = box.get("loop"), box.get("task")
        if loop is not None and task is not None:
            try:
                loop.call_soon_threadsafe(task.cancel)
            except RuntimeError:  # the loop has already closed
                pass
        # Give the client time to close its connections.
        done.wait(_CANCEL_GRACE_SECONDS)
        raise

    if "error" in box:
        error = box.pop("error")
        try:
            raise error
        finally:
            # Break the frame -> error -> traceback -> frame cycle.
            del error
    return box["result"]


def read_drawing_sync(
    drawing: Union[BufferedReader, bytes, BytesIO], asks: list[AskUnion]
) -> list[TechreadMessage]:
    """Read a drawing and wait for the answers, without async code.

    Works with or without a running event loop. Without one, the read runs on
    the calling thread. Inside a running event loop (a Jupyter or IPython
    cell, or async code) the read runs on its own event loop in a helper
    thread, and the calling thread, including its event loop, is blocked
    until the read ends. In async code prefer the async client instead:
    ``async with Werk24Client() as client:`` and
    ``client.read_drawing(drawing, asks)``.

    Interrupting the call (for example a notebook's "interrupt kernel")
    cancels the read and closes its connection.

    Args:
        drawing (Union[BufferedReader, bytes, BytesIO]): The drawing to read.
        asks (list[AskUnion]): What to extract from the drawing.

    Returns:
        list[TechreadMessage]: The ASK messages, one per answer. Progress
        messages are left out.

    Raises:
        Exception: Whatever the client raises, unchanged, for example
            InvalidLicenseException when no license is found.
    """
    from werk24.techread import Werk24Client  # import here to avoid circular imports

    async def run():
        async with Werk24Client() as client:
            return [
                msg
                async for msg in client.read_drawing(drawing, asks)
                if msg.message_type == TechreadMessageType.ASK
            ]

    return _run_blocking(run)


def read_example_drawing(asks: list[AskUnion]):
    drawing = get_test_drawing()
    try:
        responses = read_drawing_sync(drawing, asks)
    finally:
        # get_test_drawing() opens a file handle; always close it.
        drawing.close()

    results = defaultdict(list)
    for msg in responses:
        if msg.message_type == TechreadMessageType.ASK:
            results[msg.message_subtype].append(msg)

    return results
