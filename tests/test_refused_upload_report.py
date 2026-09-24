"""A drawing S3 refuses is reported per ask, not as a TypeError.

``read_drawing`` turns a refused upload into one ASK message per ask, each
carrying a ``TechreadException`` model. ``werk24.techread`` took that name from
``werk24``, where ``from werk24.utils import *`` shadows the model with the
exception class of the same name. Since the client is imported lazily
(9c99d32), it always sees the shadowed one, and every refused upload raised
``TypeError: ... unexpected keyword argument 'exception_level'``.
"""

import pytest

from werk24 import TechreadExceptionType, TechreadMessageType
from werk24.models.v2.asks import AskBalloons
from werk24.models.v2.internal import TechreadException as TechreadExceptionModel
from werk24.techread import Werk24Client
from werk24.utils.exceptions import BadRequestException, RequestTooLargeException


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "refusal", [RequestTooLargeException("x"), BadRequestException("x")]
)
async def test_a_refused_upload_yields_one_exception_message_per_ask(refusal):
    asks = [AskBalloons(), AskBalloons()]

    messages = [
        m async for m in Werk24Client._trigger_asks_exception(asks, refusal)
    ]

    assert len(messages) == len(asks)
    for message in messages:
        assert message.message_type == TechreadMessageType.ASK
        (exception,) = message.exceptions
        assert isinstance(exception, TechreadExceptionModel)
        assert (
            exception.exception_type
            == TechreadExceptionType.DRAWING_FILE_SIZE_TOO_LARGE
        )
