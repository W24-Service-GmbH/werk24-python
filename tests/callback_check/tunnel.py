"""A short-lived public HTTPS URL for a server bound to loopback.

A GitHub Actions runner has no inbound address, so the production API cannot
post a callback to it. A Cloudflare quick tunnel closes that gap: ``cloudflared
tunnel --url`` dials out to Cloudflare, is handed an ephemeral
``*.trycloudflare.com`` hostname, and forwards what arrives there to a local
port. It needs no account and no credential, which is the whole reason this
check can live in the repository rather than behind deployed infrastructure.

Two properties of that arrangement drive the code below:

- **The hostname is announced, not chosen.** It appears in cloudflared's log
  output and nowhere else, so the process's output has to be read (stderr
  is merged into stdout so one reader sees all of it).
- **The URL exists before it works.** Cloudflare announces the hostname as soon
  as it is allocated, and there is a short window afterwards in which a request
  to it still fails. Handing that URL to the API inside the window would spend
  a billable read on a callback that was never deliverable, so
  :meth:`QuickTunnel.__aenter__` does not return until it has driven a request
  through the tunnel itself.
"""

from __future__ import annotations

import asyncio
import collections
import os
import re
import shutil
from types import TracebackType
from typing import Deque, Optional, Type

import aiohttp

__all__ = ["QuickTunnel", "TunnelUnavailable", "cloudflared_binary"]

# cloudflared prints the hostname inside a boxed banner, so the pattern has to
# survive surrounding box-drawing characters and whitespace.
_URL_PATTERN = re.compile(rb"https://[-a-z0-9]+\.trycloudflare\.com")

_LOG_TAIL_LINES = 40
"""How much of cloudflared's output to keep for a failure message.

Bounded, and read continuously, for the same reason: an unread pipe fills and
blocks the process writing into it, which would hang the tunnel rather than
merely lose its logs.
"""


class TunnelUnavailable(RuntimeError):
    """Raised when no tunnel could be established.

    Carries the tail of cloudflared's output, because the useful half of
    diagnosing this ("could not connect to Cloudflare", "no such binary",
    a rate-limit notice) is only ever in that log.
    """


def cloudflared_binary() -> Optional[str]:
    """Locate the cloudflared executable.

    ``W24_CLOUDFLARED_BIN`` takes precedence, so a CI job that downloads the
    binary to a working directory does not have to put it on ``PATH``.

    Returns:
    -------
    - Optional[str]: Path to the executable, or None if there is none. None is
      the signal the callback check skips on -- absence of the tool is not a
      failure of the API.
    """
    override = os.getenv("W24_CLOUDFLARED_BIN")
    if override:
        return override if os.path.isfile(override) else None
    return shutil.which("cloudflared")


class QuickTunnel:
    """Publish ``http://127.0.0.1:<port>`` at a temporary HTTPS address.

    Used as an async context manager::

        async with QuickTunnel(receiver.port, health_path="/health") as tunnel:
            ...   # tunnel.url is public, and proven to carry traffic

    On exit the cloudflared process is stopped and the hostname stops
    resolving, so nothing outlives the check.
    """

    def __init__(
        self,
        port: int,
        health_path: str = "/health",
        startup_timeout: float = 60.0,
        probe_floor: float = 15.0,
        binary: Optional[str] = None,
    ) -> None:
        """
        Args:
        ----
        - port (int): The local port to publish.
        - health_path (str): A path on that port answering 200 to a GET. Used
          to prove the tunnel end to end before the caller relies on it.
        - startup_timeout (float): Seconds allowed for the hostname to be
          announced *and* to start carrying traffic, in total.
        - probe_floor (float): Seconds always left for the traffic probe, even
          when the hostname wait consumed the whole budget. Without it a slow
          announcement would be reported as a route that never came up.
        - binary (Optional[str]): Override the executable to run.
        """
        self.port = port
        self.health_path = health_path
        self.startup_timeout = startup_timeout
        self.probe_floor = probe_floor
        self._binary = binary or cloudflared_binary()
        self._process: Optional[asyncio.subprocess.Process] = None
        self._reader: Optional[asyncio.Task] = None
        self._log: Deque[bytes] = collections.deque(maxlen=_LOG_TAIL_LINES)
        self._url: Optional[str] = None
        self._url_found = asyncio.Event()

    @property
    def url(self) -> str:
        """The public base URL, without a trailing slash."""
        if self._url is None:
            raise RuntimeError("QuickTunnel is not running")
        return self._url

    @property
    def log_tail(self) -> str:
        """The last lines cloudflared wrote, for failure messages."""
        return "\n".join(line.decode("utf-8", "replace") for line in self._log)

    async def _drain(self, stream: asyncio.StreamReader) -> None:
        """Consume cloudflared's output, keeping a tail and spotting the URL.

        This runs for the lifetime of the tunnel, not just until the URL is
        found: the pipe has to keep being read or the process blocks on a full
        buffer once it has logged a few hundred lines.
        """
        # Read in chunks and split the lines here rather than using
        # ``readline``, which raises on a line longer than the stream limit
        # and then leaves the oversized data in the buffer -- turning one long
        # log line into a spinning drain task that never reads the pipe again.
        buffer = b""
        while True:
            chunk = await stream.read(4096)
            if not chunk:
                if buffer:
                    self._record(buffer)
                return

            buffer += chunk
            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                self._record(line)

            # A banner without a trailing newline yet: match against what is
            # buffered so the URL is not held up by the next log line.
            if self._url is None and buffer:
                self._record(buffer, keep=True)

    def _record(self, line: bytes, keep: bool = False) -> None:
        """Note a log line and check it for the tunnel hostname.

        ``keep`` is for a partial line still sitting in the buffer: scan it for
        the hostname, but do not add it to the log tail, or it would appear
        twice once the rest of it arrives.
        """
        if not keep:
            self._log.append(line.rstrip())

        if self._url is None:
            match = _URL_PATTERN.search(line)
            if match:
                self._url = match.group(0).decode("ascii")
                self._url_found.set()

    async def _await_url(self, timeout: float) -> None:
        """Wait for the hostname, or for the process to give up first.

        Raced against the process exiting rather than simply waited out: a
        cloudflared that dies on startup -- a missing binary dependency, a
        rate limit, no egress at all -- would otherwise burn the whole
        timeout before reporting a failure it already knew about.
        """
        assert self._process is not None  # noqa: B101,S101

        url_found = asyncio.ensure_future(self._url_found.wait())
        exited = asyncio.ensure_future(self._process.wait())
        try:
            done, _ = await asyncio.wait(
                {url_found, exited},
                timeout=timeout,
                return_when=asyncio.FIRST_COMPLETED,
            )
        finally:
            for task in (url_found, exited):
                task.cancel()
            await asyncio.gather(url_found, exited, return_exceptions=True)

        if self._url is not None:
            return

        if exited in done:
            raise TunnelUnavailable(
                f"cloudflared exited with code {self._process.returncode} "
                "before announcing a tunnel hostname.\n"
                f"--- cloudflared output ---\n{self.log_tail}"
            )

        raise TunnelUnavailable(
            "cloudflared did not announce a tunnel hostname within "
            f"{timeout:.0f}s.\n--- cloudflared output ---\n{self.log_tail}"
        )

    async def _await_traffic(self, deadline: float) -> None:
        """Poll the tunnel until a request actually reaches the local server.

        A 404 or a 502 here is Cloudflare answering for a route that is not
        live yet, so only a 200 counts. The loop is what separates "the
        hostname was printed" from "the hostname works", and skipping it is
        what would waste a paid read.
        """
        probe = f"{self.url}{self.health_path}"
        timeout = aiohttp.ClientTimeout(total=10)
        last_error = "no attempt completed"

        # A floor under whatever the hostname wait left behind. Waiting for the
        # announcement is the slow half and can eat the whole budget; reporting
        # "never carried traffic" without having had time to try would blame
        # the route for the delay.
        deadline = max(deadline, asyncio.get_running_loop().time() + self.probe_floor)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            while asyncio.get_running_loop().time() < deadline:
                try:
                    async with session.get(probe) as response:
                        if response.status == 200:
                            return
                        last_error = f"HTTP {response.status}"
                except (aiohttp.ClientError, asyncio.TimeoutError) as exception:
                    last_error = f"{type(exception).__name__}: {exception}"
                await asyncio.sleep(1.0)

        raise TunnelUnavailable(
            f"Tunnel {self.url} was announced but never carried traffic "
            f"(last attempt: {last_error}).\n"
            f"--- cloudflared output ---\n{self.log_tail}"
        )

    async def __aenter__(self) -> "QuickTunnel":
        if self._binary is None:
            raise TunnelUnavailable(
                "cloudflared was not found. Install it, or point "
                "W24_CLOUDFLARED_BIN at the executable."
            )

        self._process = await asyncio.create_subprocess_exec(
            self._binary,
            "tunnel",
            "--url",
            f"http://127.0.0.1:{self.port}",
            "--no-autoupdate",
            # QUIC is cloudflared's default and needs outbound UDP/7844, which
            # is the first thing a restrictive network drops. http2 rides the
            # same TCP/443 as everything else in CI.
            "--protocol",
            "http2",
            "--loglevel",
            "info",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
        )

        assert self._process.stdout is not None  # noqa: B101,S101
        self._reader = asyncio.create_task(self._drain(self._process.stdout))

        loop = asyncio.get_running_loop()
        deadline = loop.time() + self.startup_timeout
        try:
            await self._await_url(timeout=self.startup_timeout)
            await self._await_traffic(deadline=deadline)
        except BaseException:
            # Including TunnelUnavailable: a half-started tunnel must not
            # leave a cloudflared process behind for the rest of the session.
            await self.__aexit__(None, None, None)
            raise

        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        process, self._process = self._process, None
        reader, self._reader = self._reader, None

        if process is not None and process.returncode is None:
            process.terminate()
            try:
                await asyncio.wait_for(process.wait(), timeout=10)
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()

        if reader is not None:
            reader.cancel()
            # The drain task owns the pipe; let it finish unwinding before the
            # transport is collected, or asyncio reports it at GC instead.
            await asyncio.gather(reader, return_exceptions=True)

        self._url = None
        self._url_found.clear()
