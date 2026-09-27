"""Handling the errors ``Werk24Client`` raises.

Every exception below is a subclass of
``werk24.utils.exceptions.TechreadException``. What each one means, and
whether sending the request again can help:

- ``InvalidLicenseException``: no usable API key was found, or the key
  passed is not an API key. Its subclass ``LicenseNotFoundException`` lists
  every place the client looked. Pass ``token=`` to ``Werk24Client``, set
  ``W24TECHREAD_AUTH_TOKEN`` or run ``werk24 init``. Do not retry.
- ``ApiKeyRejectedException``: the API refused the key, when the connection
  opens (403) or in ``read_drawing_with_callback`` (401). The message names
  the key by its last four characters and says where it was read from.
  Replace the key. Do not retry. It is an ``UnauthorizedException``, so
  catch it before one.
- ``UnauthorizedException``: any other refusal as not authorized (401 to
  403), for example a forbidden action or an upload or download link that
  is no longer valid. Do not retry the same request.
- ``InsufficientCreditsException``: the account's request quota is used up
  (HTTP 429, or the same refusal on the connection ``read_drawing`` uses).
  It does not reset by waiting, so do not retry; top up the account first.
  It is a ``ServerException``, so catch it before one.
- ``PriorityTooHighError`` and ``InvalidPriorityError``: the ``priority``
  argument is above the account's tier, or not one of PRIO1, PRIO2, PRIO3.
- ``BadRequestException``: the request was refused as malformed, for
  example an ask type the client does not know.
- ``UnsupportedMediaType``: the drawing is not ``bytes`` or a binary file
  object, or its file format is refused.
- ``DrawingTooLargeException``: raised by
  ``Werk24Client.check_drawing_size``, which you can call before
  ``read_drawing`` to get an exception instead of the per-ask report
  described below. It is a ``RequestTooLargeException``.
- ``CallbackDrawingTooLargeException`` and
  ``CallbackFieldsTooLargeException``: ``read_drawing_with_callback``
  refused the request before sending it. Both are
  ``RequestTooLargeException``.
- ``SSLCertificateError``: the certificate of the upload could not be
  verified, often because a proxy inspects the traffic. Its message lists
  what to check. Do not retry until that is fixed.
- ``ReadTimeoutError``: the read did not finish in time, or the server went
  quiet. Worth a bounded retry.
- ``RetryableServerError``: a server error (5xx) that outlasted the
  client's own retries. Worth a bounded retry.
- ``ServerException``: any other server-side failure, such as a connection
  that closed during the read. Report it with its message.

A problem with the drawing itself is not raised. ``read_drawing`` yields
the ASK message as usual, and its ``exceptions`` list says what went wrong
(for example ``DRAWING_FILE_SIZE_TOO_LARGE``). An ERROR-level entry means
that ask has no result; a WARNING-level one leaves the result standing.

``W24AuthenticationError``, ``W24ValidationError``, ``W24RateLimitError``
and ``W24ServerError`` are not raised by the client, so this example does
not catch them.

Run it with an API key configured to read the drawing bundled with the
package:

    python examples/exception_handling.py
"""

import asyncio
import random
import sys
from typing import Awaitable, Callable, List, Optional, Tuple, Type, TypeVar

from werk24 import (
    AskMetaData,
    TechreadMessage,
    TechreadMessageType,
    Werk24Client,
    get_test_drawing,
)

# Imported from werk24.utils.exceptions rather than from werk24: the
# package also exports a data model named TechreadException, the entry an
# ASK message carries in its ``exceptions`` list.
from werk24.utils.exceptions import (
    ApiKeyRejectedException,
    BadRequestException,
    CallbackDrawingTooLargeException,
    CallbackFieldsTooLargeException,
    DrawingTooLargeException,
    InsufficientCreditsException,
    InvalidLicenseException,
    InvalidPriorityError,
    LicenseNotFoundException,
    PriorityTooHighError,
    ReadTimeoutError,
    RequestTooLargeException,
    RetryableServerError,
    ServerException,
    SSLCertificateError,
    TechreadException,
    UnauthorizedException,
    UnsupportedMediaType,
)

T = TypeVar("T")

#: The only failures this example sends again. Everything else is a
#: request, a key or an account that has to change first.
RETRYABLE: Tuple[Type[TechreadException], ...] = (
    RetryableServerError,
    ReadTimeoutError,
)

#: What to tell a user, most specific class first. The first entry the
#: exception is an instance of wins, so a subclass must come before its
#: base class (InsufficientCreditsException before ServerException).
ADVICE: Tuple[Tuple[Type[TechreadException], str], ...] = (
    (
        LicenseNotFoundException,
        "No API key is configured. Run 'werk24 init', set "
        "W24TECHREAD_AUTH_TOKEN or pass token= to Werk24Client. Every place "
        "the client looked is listed below.",
    ),
    (
        InvalidLicenseException,
        "The API key cannot be used, for the reason below. Pass a valid key "
        "with token=, set W24TECHREAD_AUTH_TOKEN or run 'werk24 init'.",
    ),
    (
        ApiKeyRejectedException,
        "The API key was refused. Replace the key named below.",
    ),
    (
        UnauthorizedException,
        "The request was refused as not authorized. Check the API key and "
        "what its account may do.",
    ),
    (
        InsufficientCreditsException,
        "The account's request quota is used up. It does not reset by "
        "waiting; top up the account before sending more requests.",
    ),
    (
        PriorityTooHighError,
        "The requested priority is above the account's tier.",
    ),
    (InvalidPriorityError, "The priority must be PRIO1, PRIO2 or PRIO3."),
    (
        DrawingTooLargeException,
        "The drawing is larger than read_drawing uploads. Reduce the file "
        "size as described below.",
    ),
    (
        CallbackDrawingTooLargeException,
        "The drawing is too large for read_drawing_with_callback. Use "
        "read_drawing, which uploads it separately.",
    ),
    (
        CallbackFieldsTooLargeException,
        "The callback headers, public key and filename leave no room for "
        "the drawing. Send fewer or shorter ones.",
    ),
    (
        RequestTooLargeException,
        "The request is larger than the service accepts.",
    ),
    (BadRequestException, "The request was refused as malformed."),
    (UnsupportedMediaType, "The drawing's type or file format is not accepted."),
    (
        SSLCertificateError,
        "The connection's certificate could not be verified. Fix the network "
        "or certificate store as described below before trying again.",
    ),
    (ReadTimeoutError, "The read did not finish in time. Try again later."),
    (
        RetryableServerError,
        "The service returned a server error. Try again later.",
    ),
    (
        ServerException,
        "The request failed on the server side. If it persists, contact "
        "support@werk24.io with the details below.",
    ),
    (TechreadException, "The request failed."),
)


def is_retryable(exception: BaseException) -> bool:
    """Whether sending the same request again can help."""
    return isinstance(exception, RETRYABLE)


def advice_for(exception: TechreadException) -> str:
    """One line for a user: the error's heading and what to do, then the details."""
    advice = next(text for cls, text in ADVICE if isinstance(exception, cls))
    return f"{exception.cli_message_header}: {advice}\n{exception}"


async def with_retries(
    attempt: Callable[[], Awaitable[T]],
    attempts: int = 3,
    base_delay: float = 2.0,
    sleep: Callable[[float], Awaitable[None]] = asyncio.sleep,
) -> T:
    """Run ``attempt`` again after a retryable failure, at most ``attempts`` times.

    Every other exception is raised at once. Each attempt is a new request.
    The delay doubles each time and is jittered, so many clients that failed
    together do not come back together.
    """
    if attempts < 1:
        raise ValueError("attempts must be at least 1")
    number = 1
    while True:
        try:
            return await attempt()
        except RETRYABLE as exception:
            if number >= attempts:
                raise
            delay = base_delay * 2 ** (number - 1) * random.uniform(0.5, 1.5)
            print(
                f"Attempt {number} of {attempts} failed "
                f"({exception.cli_message_header}); retrying in {delay:.1f}s"
            )
            await sleep(delay)
            number += 1


def _text(value: object) -> str:
    """An enum member's value, or the value itself.

    A type or subtype this client version does not know yet arrives as
    plain text rather than as an enum member.
    """
    return str(getattr(value, "value", value))


async def read_metadata(drawing: bytes) -> List[TechreadMessage]:
    """Read the title block and report per-ask problems without raising."""
    results = []
    async with Werk24Client() as client:
        async for message in client.read_drawing(drawing, [AskMetaData()]):
            if message.message_type != TechreadMessageType.ASK:
                continue
            for problem in message.exceptions:
                print(
                    f"{_text(message.message_subtype)}: "
                    f"{_text(problem.exception_level)} "
                    f"{_text(problem.exception_type)}"
                )
            results.append(message)
    return results


async def submit_for_callback(drawing: bytes, callback_url: str) -> Optional[str]:
    """Hand a drawing to ``read_drawing_with_callback``, once.

    Not wrapped in ``with_retries``: the client does not retry this call
    itself, and a server error here does not say whether the request was
    accepted before it failed, so sending it again can start a second read.
    """
    try:
        client = Werk24Client()
        request_id = await client.read_drawing_with_callback(
            drawing, [AskMetaData()], callback_url
        )
    except TechreadException as exception:
        print(advice_for(exception))
        return None
    return str(request_id)


async def main() -> int:
    with get_test_drawing() as file:
        drawing = file.read()
    try:
        messages = await with_retries(lambda: read_metadata(drawing))
    except TechreadException as exception:
        print(advice_for(exception))
        return 1
    print(f"Received {len(messages)} ASK message(s).")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
