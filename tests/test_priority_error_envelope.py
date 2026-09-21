"""Priority refusals have to survive the envelope the API actually sends.

``_parse_message`` recognised priority errors by a top-level ``error`` key::

    {"error": "PRIORITY_TOO_HIGH", "message": ..., "details": {...}}

crew-api never sends that. Every refusal it returns goes through
``utils.error_responses.create_error_response``, which builds an
``ErrorResponse`` of ``code`` / ``message`` / ``details`` / ``request_id`` and
nothing else. So both priority refusals fell through to the generic
``ServerException`` -- the one whose message tells the customer the Werk24
service team has been notified -- for a 4xx that is theirs to fix and that the
API exists to return.

The HTTPS side had the matching gap: ``_raise_for_status`` is handed the status
code alone, so a priority refusal on ``read_drawing_with_callback`` surfaced as
a bare ``UnauthorizedException`` or ``BadRequestException`` with the tiers
dropped, even though that method documents both typed exceptions.

The bodies below are copied from what crew-api produces; see
``utils/error_responses.py`` in that repo.
"""

import json
from unittest import mock

import pytest

from werk24 import AskMetaData
from werk24.techread import Werk24Client
from werk24.utils.exceptions import (
    BadRequestException,
    InvalidPriorityError,
    PriorityTooHighError,
    ServerException,
    UnauthorizedException,
)


def _too_high(account_tier="PRIO3", requested="PRIO1"):
    """The body crew-api's error_403_priority_too_high returns."""
    return {
        "code": "403",
        "message": f"Requested priority {requested} exceeds account tier {account_tier}",
        "details": {
            "account_tier": account_tier,
            "requested_priority": requested,
        },
        "request_id": "3f7d1d1e-0000-4000-8000-000000000000",
    }


def _invalid(value="URGENT"):
    """The body crew-api's error_400_bad_request returns for a bad priority."""
    return {
        "code": "400",
        "message": f"Invalid priority value: {value}",
        "details": {"error": "INVALID_PRIORITY"},
    }


class _FakeResponse:
    """The two things ``_raise_for_priority_error`` touches on a response."""

    def __init__(self, status, payload, raises=None):
        self.status = status
        self._payload = payload
        self._raises = raises
        #: Set by the context manager's exit. A pooled session only pools if
        #: every response gives its connection back.
        self.released = False

    async def json(self, content_type=None):
        if self._raises is not None:
            raise self._raises
        return self._payload


class TestTheWebsocketPathParsesTheRealEnvelope:
    def test_a_403_with_both_tiers_is_a_priority_error(self):
        with pytest.raises(PriorityTooHighError) as exc:
            Werk24Client._parse_message(json.dumps(_too_high()))
        assert exc.value.account_tier == "PRIO3"
        assert exc.value.requested_priority == "PRIO1"

    def test_the_invalid_value_detail_is_a_priority_error(self):
        with pytest.raises(InvalidPriorityError):
            Werk24Client._parse_message(json.dumps(_invalid()))

    def test_an_ordinary_403_is_still_not_a_priority_error(self):
        """Both detail keys are required, so a plain Forbidden cannot match."""
        body = {"code": "403", "message": "Forbidden", "details": {}}
        with pytest.raises(UnauthorizedException):
            Werk24Client._parse_message(json.dumps(body))

    def test_a_403_naming_only_one_tier_is_not_a_priority_error(self):
        body = {
            "code": "403",
            "message": "Account is suspended",
            "details": {"account_tier": "PRIO3"},
        }
        with pytest.raises(ServerException):
            Werk24Client._parse_message(json.dumps(body))

    def test_an_unrelated_400_is_still_not_a_priority_error(self):
        body = {
            "code": "400",
            "message": "Invalid request data",
            "details": {"error": "something else"},
        }
        with pytest.raises(ServerException):
            Werk24Client._parse_message(json.dumps(body))


class TestTheOlderFormStillWorks:
    """A client may run against a server that does send a top-level ``error``."""

    def test_top_level_priority_too_high(self):
        body = {
            "error": "PRIORITY_TOO_HIGH",
            "message": "Requested priority PRIO1 exceeds account tier PRIO2",
            "details": {"account_tier": "PRIO2", "requested_priority": "PRIO1"},
        }
        with pytest.raises(PriorityTooHighError) as exc:
            Werk24Client._parse_message(json.dumps(body))
        assert exc.value.account_tier == "PRIO2"

    def test_top_level_invalid_priority_keeps_naming_the_value(self):
        body = {
            "error": "INVALID_PRIORITY",
            "message": "Invalid priority value: URGENT",
            "details": {"priority": "URGENT"},
        }
        with pytest.raises(InvalidPriorityError) as exc:
            Werk24Client._parse_message(json.dumps(body))
        assert exc.value.invalid_value == "URGENT"


class TestTheMapperItself:
    def test_a_non_mapping_body_is_not_a_refusal(self):
        for payload in (None, [], "PRIO3", 3):
            assert Werk24Client._priority_exception(payload) is None

    def test_a_non_mapping_details_does_not_explode(self):
        body = {"code": "403", "message": "nope", "details": "not a dict"}
        assert Werk24Client._priority_exception(body) is None

    def test_the_requested_value_fills_in_the_invalid_one(self):
        """The current envelope names the value only in prose."""
        exc = Werk24Client._priority_exception(_invalid(), "PRIO4")
        assert isinstance(exc, InvalidPriorityError)
        assert exc.invalid_value == "PRIO4"

    def test_the_server_value_wins_over_the_requested_one(self):
        body = {
            "code": "400",
            "message": "Invalid priority value: URGENT",
            "details": {"error": "INVALID_PRIORITY", "priority": "URGENT"},
        }
        exc = Werk24Client._priority_exception(body, "PRIO4")
        assert exc.invalid_value == "URGENT"


@pytest.mark.asyncio
class TestTheCallbackPathRaisesTypedExceptions:
    async def test_a_403_becomes_a_priority_error_not_an_auth_error(self):
        response = _FakeResponse(403, _too_high("PRIO2", "PRIO1"))
        with pytest.raises(PriorityTooHighError) as exc:
            await Werk24Client._raise_for_priority_error(response)
        assert exc.value.account_tier == "PRIO2"
        assert exc.value.requested_priority == "PRIO1"

    async def test_a_400_becomes_a_priority_error_naming_what_was_sent(self):
        response = _FakeResponse(400, _invalid())
        with pytest.raises(InvalidPriorityError) as exc:
            await Werk24Client._raise_for_priority_error(response, "PRIO4")
        assert exc.value.invalid_value == "PRIO4"

    async def test_an_unrelated_4xx_falls_through_to_the_status_mapping(self):
        """Returning lets ``_raise_for_status`` answer, as it did before."""
        response = _FakeResponse(400, {"code": "400", "message": "nope"})
        await Werk24Client._raise_for_priority_error(response)

        with pytest.raises(BadRequestException):
            Werk24Client._raise_for_status("https://example.com", 400)

    async def test_a_status_that_is_never_a_priority_refusal_is_not_read(self):
        """A 500 body is not worth decoding, so it must not even be touched."""
        response = _FakeResponse(500, None, raises=AssertionError("body was read"))
        await Werk24Client._raise_for_priority_error(response)

    async def test_an_undecodable_body_is_left_to_the_status_mapping(self):
        response = _FakeResponse(403, None, raises=ValueError("not json"))
        await Werk24Client._raise_for_priority_error(response)


class _ResponseContext:
    """What aiohttp's ``session.post(...)`` actually returns.

    It is a ``_RequestContextManager``: awaitable *and* an async context
    manager. The stand-in below was only awaitable, so it would have kept
    passing if the client stopped releasing its responses, which is the thing
    a pooled session depends on.
    """

    def __init__(self, response):
        self._response = response

    def __await__(self):
        async def _resolve():
            return self._response

        return _resolve().__await__()

    async def __aenter__(self):
        return self._response

    async def __aexit__(self, *exc):
        self._response.released = True
        return False


class _FakeSession:
    """The two things ``read_drawing_with_callback`` asks of a session."""

    def __init__(self, response):
        self._response = response
        self.calls = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc):
        return False

    def post(self, url, data=None, headers=None):
        self.calls.append(url)
        return _ResponseContext(self._response)


async def _call_with_callback(client, response, priority):
    """Drive the real ``read_drawing_with_callback`` against *response*."""
    session = _FakeSession(response)
    with mock.patch.object(client, "_make_https_session", return_value=session):
        return await client.read_drawing_with_callback(
            b"%PDF-1.7\n% a drawing\n",
            asks=[AskMetaData()],
            callback_url="https://example.com/webhook",
            priority=priority,
        )


@pytest.mark.asyncio
class TestReadDrawingWithCallbackIsActuallyWired:
    """The mapping has to be reachable from the public method, not just exist.

    Testing ``_raise_for_priority_error`` on its own leaves the one line that
    calls it, and the ``validated_priority`` it passes, free to regress without
    a single test noticing. These drive the real method.
    """

    async def test_a_403_propagates_as_a_priority_error(self):
        client = Werk24Client(token="t", region="r")
        response = _FakeResponse(403, _too_high("PRIO2", "PRIO1"))
        with pytest.raises(PriorityTooHighError) as exc:
            await _call_with_callback(client, response, "PRIO1")
        assert exc.value.account_tier == "PRIO2"
        assert exc.value.requested_priority == "PRIO1"

    async def test_a_400_propagates_and_carries_the_priority_that_was_sent(self):
        """Pins the ``validated_priority`` argument, not just the call.

        The priority sent is valid as far as this client is concerned -- it
        has to be, or ``validate_priority`` would have refused it locally --
        so the only way ``invalid_value`` can read PRIO3 here is if the
        method threads what it sent into the mapper. That is exactly the
        wiring a regression would drop.
        """
        client = Werk24Client(token="t", region="r")
        response = _FakeResponse(400, _invalid())
        with pytest.raises(InvalidPriorityError) as exc:
            await _call_with_callback(client, response, "prio3")
        assert exc.value.invalid_value == "PRIO3"

    async def test_an_unrelated_403_is_still_an_auth_error(self):
        client = Werk24Client(token="t", region="r")
        response = _FakeResponse(403, {"code": "403", "message": "Forbidden"})
        with pytest.raises(UnauthorizedException):
            await _call_with_callback(client, response, "PRIO3")

    async def test_a_successful_read_is_untouched(self):
        """The body is read once for the error check and once for the result."""
        client = Werk24Client(token="t", region="r")
        request_id = "3f7d1d1e-0000-4000-8000-000000000001"
        response = _FakeResponse(200, {"request_id": request_id})
        returned = await _call_with_callback(client, response, "PRIO3")
        assert str(returned) == request_id

    async def test_the_response_is_released(self):
        """A pooled session only pools if each response gives its slot back.

        The session is shared for the client's lifetime now, so a response
        that is never released holds its connector slot until the garbage
        collector reaches it - which is the pooling this was all for.
        """
        client = Werk24Client(token="t", region="r")
        response = _FakeResponse(
            200, {"request_id": "3f7d1d1e-0000-4000-8000-000000000001"}
        )
        await _call_with_callback(client, response, "PRIO3")
        assert response.released is True

    async def test_the_response_is_released_on_the_error_path_too(self):
        client = Werk24Client(token="t", region="r")
        response = _FakeResponse(403, {"code": "403", "message": "Forbidden"})
        with pytest.raises(UnauthorizedException):
            await _call_with_callback(client, response, "PRIO3")
        assert response.released is True
