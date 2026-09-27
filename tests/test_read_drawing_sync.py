"""``read_drawing_sync`` works with and without a running event loop.

It used to end in ``asyncio.run()``, which refuses to start while an event
loop is already running in the calling thread. That is the normal state of a
Jupyter or IPython cell, and of any synchronous call made from async code, so
there the call failed with ``RuntimeError: asyncio.run() cannot be called from
a running event loop`` and a "coroutine was never awaited" warning, and
nothing was read.

Now, inside a running loop, the read runs on its own event loop in a helper
thread while the calling thread waits for it. These tests pin that the result
and the exceptions are the same on both paths, that nothing is left
un-awaited, that an interrupt cancels the read instead of abandoning it, and
that the README quick start prints what it reads.

Every test here is offline: the client is replaced by ``FakeClient`` below.
"""

import asyncio
import contextvars
import gc
import json
import re
import subprocess
import sys
import textwrap
import threading
import uuid
import warnings
from io import BytesIO
from pathlib import Path
from unittest.mock import patch

import pytest

import werk24
from werk24.models import AskType, TechreadMessage, TechreadMessageType
from werk24.models.v2.internal import TechreadMessageSubtype
from werk24.models.v2.responses import ResponsePageAssessment
from werk24.utils import assets
from werk24.utils.assets import (
    _HELPER_THREAD_NAME,
    _run_blocking,
    read_drawing_sync,
    read_example_drawing,
)
from werk24.utils.exceptions import BadRequestException, InvalidLicenseException

REPO_ROOT = Path(__file__).resolve().parent.parent

#: A context variable the caller sets, to check it reaches the read.
_CALLER_LABEL: contextvars.ContextVar = contextvars.ContextVar(
    "caller_label", default=None
)


def _progress_message() -> TechreadMessage:
    return TechreadMessage(
        request_id=uuid.uuid4(),
        message_type=TechreadMessageType.PROGRESS,
        message_subtype=TechreadMessageSubtype.PROGRESS_STARTED,
    )


def _ask_message() -> TechreadMessage:
    return TechreadMessage(
        request_id=uuid.uuid4(),
        message_type=TechreadMessageType.ASK,
        message_subtype=AskType.PAGE_ASSESSMENT,
        payload_dict=ResponsePageAssessment(),
    )


class FakeClient:
    """Stands in for ``Werk24Client``: no license, no socket, two messages.

    Class attributes record what the last instance saw, so a test can check
    which thread ran the read and whether the ``async with`` block was left.
    ``reset()`` clears them; the ``fake_client`` fixture calls it.
    """

    progress: TechreadMessage
    ask: TechreadMessage
    read_thread = None
    exited = False
    caller_label = None

    @classmethod
    def reset(cls) -> None:
        cls.progress = _progress_message()
        cls.ask = _ask_message()
        cls.read_thread = None
        cls.exited = False
        cls.caller_label = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        type(self).exited = True
        return False

    async def read_drawing(self, drawing, asks):
        type(self).read_thread = threading.current_thread()
        type(self).caller_label = _CALLER_LABEL.get()
        yield type(self).progress
        yield type(self).ask


class BadRequestClient(FakeClient):
    """A client whose read fails the way a refused request does."""

    async def read_drawing(self, drawing, asks):
        type(self).read_thread = threading.current_thread()
        raise BadRequestException("refused by the fake server")
        yield  # pragma: no cover - makes this an async generator


class NoLicenseClient(FakeClient):
    """A client that cannot be built, the way a missing license fails."""

    def __init__(self):
        raise InvalidLicenseException("no license in the fake environment")


@pytest.fixture
def fake_client():
    """Patch ``FakeClient`` in where ``read_drawing_sync`` looks it up."""
    FakeClient.reset()
    with patch("werk24.techread.Werk24Client", FakeClient):
        yield FakeClient


def _drawing() -> BytesIO:
    return BytesIO(b"not a real drawing")


class TestWithoutARunningLoop:
    """The plain script case: unchanged, still ``asyncio.run()``."""

    def test_returns_only_the_ask_message(self, fake_client):
        result = read_drawing_sync(_drawing(), [])

        assert result == [fake_client.ask]
        assert result[0] is fake_client.ask

    def test_the_read_runs_on_the_calling_thread(self, fake_client):
        read_drawing_sync(_drawing(), [])

        assert fake_client.read_thread is threading.current_thread()
        assert fake_client.exited

    def test_a_client_error_keeps_its_type(self, fake_client):
        with patch("werk24.techread.Werk24Client", NoLicenseClient):
            with pytest.raises(InvalidLicenseException) as excinfo:
                read_drawing_sync(_drawing(), [])
        assert excinfo.type is InvalidLicenseException


class TestInsideARunningLoop:
    """The notebook case: a cell is already running an event loop."""

    async def test_returns_the_same_list(self, fake_client):
        asyncio.get_running_loop()  # the premise of this class

        result = read_drawing_sync(_drawing(), [])

        assert result == [fake_client.ask]
        assert result[0] is fake_client.ask

    async def test_the_read_runs_on_a_named_helper_thread(self, fake_client):
        read_drawing_sync(_drawing(), [])

        helper = fake_client.read_thread
        assert helper is not None
        assert helper is not threading.current_thread()
        assert helper.name == _HELPER_THREAD_NAME
        assert helper.daemon
        # The helper finishes with the read; nothing is left running.
        helper.join(timeout=5)
        assert not helper.is_alive()

    async def test_the_client_leaves_its_async_with_block(self, fake_client):
        read_drawing_sync(_drawing(), [])

        assert fake_client.exited

    async def test_the_calling_loop_still_works_afterwards(self, fake_client):
        read_drawing_sync(_drawing(), [])

        await asyncio.sleep(0)
        assert await asyncio.wait_for(asyncio.sleep(0, result="ok"), 1) == "ok"

    async def test_an_error_from_the_read_keeps_its_type(self, fake_client):
        BadRequestClient.reset()
        with patch("werk24.techread.Werk24Client", BadRequestClient):
            with pytest.raises(BadRequestException) as excinfo:
                read_drawing_sync(_drawing(), [])

        assert excinfo.type is BadRequestException
        assert "refused by the fake server" in str(excinfo.value)
        # The traceback still reaches the frame that raised it.
        frames = [entry.name for entry in excinfo.traceback]
        assert "read_drawing" in frames
        assert BadRequestClient.exited

    async def test_a_missing_license_is_not_turned_into_a_runtime_error(
        self, fake_client
    ):
        with patch("werk24.techread.Werk24Client", NoLicenseClient):
            with pytest.raises(InvalidLicenseException) as excinfo:
                read_drawing_sync(_drawing(), [])

        assert excinfo.type is InvalidLicenseException
        assert not isinstance(excinfo.value, RuntimeError)

    async def test_nothing_is_left_un_awaited(self, fake_client):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            read_drawing_sync(_drawing(), [])
            with patch("werk24.techread.Werk24Client", NoLicenseClient):
                with pytest.raises(InvalidLicenseException):
                    read_drawing_sync(_drawing(), [])
            gc.collect()

        never_awaited = [
            str(w.message)
            for w in caught
            if issubclass(w.category, RuntimeWarning)
            and "never awaited" in str(w.message)
        ]
        assert never_awaited == []

    async def test_the_callers_context_variables_reach_the_read(self, fake_client):
        _CALLER_LABEL.set("from-the-cell")

        async def read_label():
            return _CALLER_LABEL.get()

        assert _run_blocking(read_label) == "from-the-cell"

        read_drawing_sync(_drawing(), [])
        assert fake_client.caller_label == "from-the-cell"

    async def test_read_example_drawing_closes_the_drawing(
        self, fake_client, monkeypatch
    ):
        drawing = _drawing()
        monkeypatch.setattr(assets, "get_test_drawing", lambda: drawing)

        result = read_example_drawing([])

        assert dict(result) == {AskType.PAGE_ASSESSMENT: [fake_client.ask]}
        assert drawing.closed


_INTERRUPT_SCRIPT = textwrap.dedent(
    """
    import asyncio
    import json
    import os
    import signal
    import threading
    import time

    from werk24.utils.assets import _run_blocking

    # What a notebook kernel has: Ctrl-C / "interrupt kernel" raises
    # KeyboardInterrupt in the main thread. Set explicitly, because a process
    # started in the background may inherit SIGINT as ignored.
    signal.signal(signal.SIGINT, signal.default_int_handler)

    cleanup_ran = threading.Event()


    async def slow():
        try:
            await asyncio.sleep(60)
        finally:
            cleanup_ran.set()


    async def cell():
        threading.Timer(0.3, os.kill, (os.getpid(), signal.SIGINT)).start()
        start = time.monotonic()
        try:
            _run_blocking(slow)
        except KeyboardInterrupt:
            interrupted = True
        else:
            interrupted = False
        print(json.dumps({
            "interrupted": interrupted,
            "elapsed": time.monotonic() - start,
            "cleanup_ran": cleanup_ran.is_set(),
        }))


    # Not asyncio.run(): from 3.11 on it installs its own SIGINT handler that
    # cancels the main task instead of raising KeyboardInterrupt, which is
    # not what a notebook does.
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(cell())
    finally:
        loop.close()
    """
)


@pytest.mark.skipif(sys.platform == "win32", reason="sends SIGINT with os.kill")
def test_an_interrupt_cancels_the_read_instead_of_abandoning_it():
    """Interrupting the kernel stops the read and lets it clean up.

    Runs in a subprocess because it sends SIGINT to its own process.
    """
    result = subprocess.run(
        [sys.executable, "-c", _INTERRUPT_SCRIPT],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=120,
    )

    assert result.returncode == 0, result.stderr
    outcome = json.loads(result.stdout.strip().splitlines()[-1])
    assert outcome["interrupted"] is True
    assert outcome["elapsed"] < 10
    assert outcome["cleanup_ran"] is True


def _quick_start_blocks() -> list:
    """The python code blocks in the README's "Quick Start" section."""
    readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    section = readme.split("\n## Quick Start\n", 1)[1]
    section = re.split(r"\n## ", section, maxsplit=1)[0]
    return re.findall(r"```python\n(.*?)```", section, flags=re.DOTALL)


class TestTheReadmeQuickStart:
    """The quick start is copied more than any other code; it must work."""

    def test_the_section_has_both_examples(self):
        blocks = _quick_start_blocks()
        assert len(blocks) >= 2
        assert "Werk24Client" in blocks[0]
        assert "read_drawing_sync" in blocks[1]

    @pytest.mark.parametrize("index", [0, 1], ids=["async", "sync"])
    def test_the_example_prints_a_json_answer(self, index, fake_client, capsys):
        code = _quick_start_blocks()[index]

        with patch.object(werk24, "Werk24Client", FakeClient, create=True):
            exec(compile(code, "README.md", "exec"), {"__name__": "__main__"})

        printed = capsys.readouterr().out.strip()
        answer, end = json.JSONDecoder().raw_decode(printed)
        assert isinstance(answer, dict)
        assert set(answer) == {"message_subtype", "payload_dict"}
        assert answer["message_subtype"] == AskType.PAGE_ASSESSMENT.value
        # Exactly one answer: the progress message is not printed.
        assert printed[end:].strip() == ""
