"""A local HTTP server that records the callbacks Werk24 posts to it.

This module records; it does not judge. Everything it captures is kept raw --
the undecoded body and the headers exactly as they arrived -- so that the
contract checks in :mod:`tests.callback_check.contract` can assert on the bytes
on the wire rather than on something this file already normalised. A receiver
that parsed the payload before storing it could not tell the difference between
a malformed message and its own leniency.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from types import TracebackType
from typing import Callable, Dict, List, Optional, Sequence, Type

from aiohttp import web

__all__ = ["CallbackDelivery", "CallbackReceiver"]


@dataclass(frozen=True)
class CallbackDelivery:
    """One HTTP request that reached the receiver.

    Attributes:
    ----------
    - method (str): The HTTP method used.
    - path (str): The path the request was sent to.
    - headers (Dict[str, str]): Request headers, lower-cased. A header sent
      more than once keeps its last value; the callback contract has no
      repeated headers, so collapsing them loses nothing and makes the
      assertions readable.
    - body (bytes): The raw request body, undecoded.
    - received_at (float): ``time.monotonic()`` when the body had been read.
      Monotonic rather than wall clock, because the only thing ever asked of
      it is the ordering of two deliveries.
    """

    method: str
    path: str
    headers: Dict[str, str]
    body: bytes
    received_at: float = field(compare=False)


class CallbackReceiver:
    """An HTTP server on loopback that accepts callbacks and remembers them.

    Bound to ``127.0.0.1`` on an ephemeral port: it is never reachable from
    outside the machine on its own. :class:`~tests.callback_check.tunnel.QuickTunnel`
    is what gives it a public address, and only for as long as the check runs.

    Used as an async context manager::

        async with CallbackReceiver() as receiver:
            ...                                   # receiver.port is now bound
        # server closed, deliveries still readable

    The recorded deliveries survive the context manager's exit, so the
    assertions can run after the server is down.
    """

    def __init__(self, path: str = "/callback", health_path: str = "/health") -> None:
        """
        Args:
        ----
        - path (str): The path callbacks are expected on. Anything posted
          elsewhere is still recorded -- a callback that arrives at the wrong
          path is evidence, not noise, and dropping it would leave the check
          reporting "no callback" for a delivery that did happen.
        - health_path (str): A GET endpoint used to prove the tunnel is
          carrying traffic before a drawing is submitted. It is deliberately
          not the callback path, so a health probe can never be mistaken for
          a delivery.
        """
        self.path = path
        self.health_path = health_path
        self._deliveries: List[CallbackDelivery] = []
        self._event = asyncio.Event()
        self._runner: Optional[web.AppRunner] = None
        self._port: Optional[int] = None

    @property
    def deliveries(self) -> Sequence[CallbackDelivery]:
        """Everything recorded so far, in arrival order."""
        return tuple(self._deliveries)

    @property
    def port(self) -> int:
        """The bound port. Only valid inside the context manager."""
        if self._port is None:
            raise RuntimeError("CallbackReceiver is not running")
        return self._port

    async def _handle_callback(self, request: web.Request) -> web.Response:
        body = await request.read()
        self._deliveries.append(
            CallbackDelivery(
                method=request.method,
                path=request.path,
                headers={k.lower(): v for k, v in request.headers.items()},
                body=body,
                received_at=time.monotonic(),
            )
        )
        # Wake every waiter rather than the first one: ``wait_for`` re-checks
        # its own predicate and clears the event itself.
        self._event.set()

        # 200 with a JSON body. core-reader treats a non-2xx as a delivery
        # failure and stops sending, so a receiver that answered anything else
        # would truncate the very message sequence the check is here to
        # inspect.
        return web.json_response({"status": "ok"})

    async def _handle_health(self, _: web.Request) -> web.Response:
        return web.json_response({"status": "ok"})

    async def __aenter__(self) -> "CallbackReceiver":
        app = web.Application()
        app.router.add_get(self.health_path, self._handle_health)
        # A catch-all rather than a route on ``self.path``: see the note in
        # __init__ about recording misdirected posts.
        app.router.add_route("*", "/{tail:.*}", self._handle_callback)

        self._runner = web.AppRunner(app, access_log=None)
        await self._runner.setup()
        # Port 0: the kernel picks a free one, so parallel runs never collide.
        await web.TCPSite(self._runner, host="127.0.0.1", port=0).start()

        # ``addresses`` reports what was actually bound, which is the only way
        # to learn the port the kernel chose.
        addresses = self._runner.addresses
        if not addresses:
            raise RuntimeError("CallbackReceiver failed to bind a port")
        self._port = addresses[0][1]
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc: Optional[BaseException],
        tb: Optional[TracebackType],
    ) -> None:
        if self._runner is not None:
            await self._runner.cleanup()
            self._runner = None
        self._port = None

    async def wait_for(
        self,
        predicate: Callable[[Sequence[CallbackDelivery]], bool],
        timeout: float,
    ) -> bool:
        """Wait until ``predicate`` accepts the deliveries recorded so far.

        Args:
        ----
        - predicate: Called with every delivery recorded to date, whenever one
          arrives and once before waiting at all.
        - timeout (float): Seconds to wait in total, not per delivery.

        Returns:
        -------
        - bool: True if the predicate was satisfied, False if the timeout
          expired first. It returns rather than raises because a timeout is
          not automatically a failure of the API: the caller has the recorded
          deliveries and can say something far more useful about what did and
          did not arrive than "timed out" ever could.
        """
        deadline = time.monotonic() + timeout
        while True:
            if predicate(self.deliveries):
                return True

            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return False

            self._event.clear()

            # Re-check between the clear and the await, not only after it. A
            # delivery landing in the window between the predicate call above
            # and this clear() sets the event, and the clear then throws that
            # wake-up away -- so without this the wait sleeps out its whole
            # timeout before noticing a condition that was already true. It
            # still returned the right answer, but 300s late on the paid
            # end-to-end run.
            #
            # Clear first, then check: the handler appends before it sets, so
            # any wake-up discarded above corresponds to a delivery this call
            # can already see.
            if predicate(self.deliveries):
                return True

            try:
                await asyncio.wait_for(self._event.wait(), timeout=remaining)
            except asyncio.TimeoutError:
                return predicate(self.deliveries)
