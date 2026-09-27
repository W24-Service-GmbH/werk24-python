"""The exception-handling example names only exceptions the client raises.

``examples/exception_handling.py`` used to build and catch four classes
(``W24AuthenticationError``, ``W24ValidationError``, ``W24RateLimitError``,
``W24ServerError``) that nothing in the client ever raises, and it taught a
wait-and-retry loop for HTTP 429, which the client maps to
``InsufficientCreditsException``: a used-up quota that waiting does not fix.
An ``except`` clause written from it never matched a real error.

These tests hold the example to the client: every class it handles must be
one the client constructs, the classes it never constructs must not appear,
and the retry helper must not send a request again after a quota refusal.
"""

import ast
import importlib.util
import inspect
import pathlib
import re
from unittest.mock import AsyncMock, patch

import pytest
from websockets.datastructures import Headers
from websockets.exceptions import InvalidStatus
from websockets.http11 import Response

import werk24.utils.exceptions as exceptions_module
from werk24 import Werk24Client
from werk24.techread import HTTP_EXCEPTION_CLASSES
from werk24.utils.exceptions import (
    ApiKeyRejectedException,
    BadRequestException,
    InsufficientCreditsException,
    InvalidLicenseException,
    LicenseNotFoundException,
    ReadTimeoutError,
    RetryableServerError,
    ServerException,
    SSLCertificateError,
    TechreadException,
    UnauthorizedException,
)

_ROOT = pathlib.Path(__file__).resolve().parents[1]
_EXAMPLE = _ROOT / "examples" / "exception_handling.py"
_PACKAGE = pathlib.Path(exceptions_module.__file__).resolve().parents[1]


def _load_example():
    spec = importlib.util.spec_from_file_location(
        "exception_handling_example", _EXAMPLE
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


example = _load_example()


def _exception_classes():
    return {
        name: value
        for name, value in vars(exceptions_module).items()
        if inspect.isclass(value) and issubclass(value, TechreadException)
    }


def _constructed_by_client():
    """Names of every class the package calls, outside the module defining them.

    A class only ever raised through a variable (``PriorityTooHighError`` is
    built in one method and raised in another) is still called somewhere,
    and the HTTP status map raises its values through a variable too.
    """
    names = set()
    for path in _PACKAGE.rglob("*.py"):
        if path.resolve() == pathlib.Path(exceptions_module.__file__).resolve():
            continue
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name):
                    names.add(func.id)
                elif isinstance(func, ast.Attribute):
                    names.add(func.attr)
    names |= {cls.__name__ for cls in HTTP_EXCEPTION_CLASSES.values() if cls}
    return names


def _names_in_example():
    tree = ast.parse(_EXAMPLE.read_text(encoding="utf-8"))
    return {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)} | {
        alias.name for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)
        for alias in node.names
    }


class TestTheExampleMatchesTheClient:
    def test_every_class_it_handles_is_raised_by_the_client(self):
        constructed = _constructed_by_client()
        handled = [cls for cls, _ in example.ADVICE] + list(example.RETRYABLE)
        missing = sorted(
            cls.__name__
            for cls in handled
            if cls is not TechreadException and cls.__name__ not in constructed
        )
        assert missing == []

    def test_it_names_no_class_the_client_never_raises(self):
        never = set(_exception_classes()) - _constructed_by_client()
        # The four legacy classes; the test does not depend on the list.
        assert {"W24AuthenticationError", "W24RateLimitError"} <= never
        assert never & _names_in_example() == set()

    def test_its_docstring_names_every_class_it_handles(self):
        documented = set(re.findall(r"``(?:[\w.]*\.)?(\w+)``", example.__doc__))
        handled = {cls.__name__ for cls, _ in example.ADVICE}
        assert handled - documented == set()

    def test_no_entry_is_shadowed_by_an_earlier_base_class(self):
        classes = [cls for cls, _ in example.ADVICE]
        for earlier, cls in enumerate(classes):
            for base in classes[:earlier]:
                assert not issubclass(cls, base), (cls, base)

    def test_a_used_up_quota_gets_its_own_advice(self):
        quota = example.advice_for(InsufficientCreditsException("429"))
        server = example.advice_for(ServerException("500"))
        assert "top up" in quota
        assert quota.splitlines()[0] != server.splitlines()[0]

    def test_a_refused_key_gets_its_own_advice(self):
        rejected = example.advice_for(ApiKeyRejectedException(key_suffix="abcd"))
        unauthorized = example.advice_for(UnauthorizedException("403"))
        assert "abcd" in rejected
        assert rejected.splitlines()[0] != unauthorized.splitlines()[0]

    def test_a_missing_key_names_the_environment_variable(self):
        advice = example.advice_for(LicenseNotFoundException())
        assert "W24TECHREAD_AUTH_TOKEN" in advice.splitlines()[0]

    def test_a_missing_key_gets_its_own_advice(self):
        missing = LicenseNotFoundException([("/home/me/.werk24", "not found")])
        unusable = InvalidLicenseException("it is empty")

        def advice_text(exception):
            return next(
                text for cls, text in example.ADVICE if isinstance(exception, cls)
            )

        assert advice_text(missing) != advice_text(unusable)
        assert "werk24 init" in advice_text(missing)
        assert "/home/me/.werk24: not found" in example.advice_for(missing)
        assert "it is empty" in example.advice_for(unusable)

    @pytest.mark.parametrize(
        "exception,retryable",
        [
            (RetryableServerError("503"), True),
            (ReadTimeoutError("idle"), True),
            (InsufficientCreditsException("429"), False),
            (ServerException("closed"), False),
            (UnauthorizedException("403"), False),
            (ApiKeyRejectedException(status_code=403), False),
            (BadRequestException("ask"), False),
            (InvalidLicenseException("none"), False),
            (SSLCertificateError("proxy"), False),
        ],
    )
    def test_only_transient_failures_are_retryable(self, exception, retryable):
        assert example.is_retryable(exception) is retryable


class TestWithRetries:
    async def test_a_quota_refusal_is_not_sent_again(self):
        attempt = AsyncMock(side_effect=InsufficientCreditsException("429"))
        sleep = AsyncMock()
        with pytest.raises(InsufficientCreditsException):
            await example.with_retries(attempt, attempts=3, sleep=sleep)
        assert attempt.await_count == 1
        sleep.assert_not_awaited()

    async def test_a_server_error_is_retried_until_it_succeeds(self):
        attempt = AsyncMock(
            side_effect=[RetryableServerError("503"), RetryableServerError("503"), "ok"]
        )
        sleep = AsyncMock()
        assert await example.with_retries(attempt, attempts=3, sleep=sleep) == "ok"
        assert attempt.await_count == 3
        assert sleep.await_count == 2

    async def test_the_last_timeout_is_raised(self):
        attempt = AsyncMock(side_effect=ReadTimeoutError("idle"))
        sleep = AsyncMock()
        with pytest.raises(ReadTimeoutError):
            await example.with_retries(attempt, attempts=3, sleep=sleep)
        assert attempt.await_count == 3
        assert sleep.await_count == 2

    @pytest.mark.parametrize(
        "exception",
        [ServerException("closed"), UnauthorizedException("403")],
    )
    async def test_other_failures_are_raised_at_once(self, exception):
        attempt = AsyncMock(side_effect=exception)
        with pytest.raises(type(exception)):
            await example.with_retries(attempt, sleep=AsyncMock())
        assert attempt.await_count == 1

    async def test_at_least_one_attempt(self):
        with pytest.raises(ValueError):
            await example.with_retries(AsyncMock(), attempts=0)


class TestMain:
    async def test_a_missing_token_is_reported_not_raised(self, capsys):
        with patch.object(
            example,
            "Werk24Client",
            side_effect=InvalidLicenseException("No valid license could be found."),
        ):
            assert await example.main() == 1
        assert "W24TECHREAD_AUTH_TOKEN" in capsys.readouterr().out


class TestTheClientBehaviourTheExampleRelies:
    @pytest.mark.parametrize(
        "status,expected",
        [
            (401, UnauthorizedException),
            (403, UnauthorizedException),
            (429, InsufficientCreditsException),
            (503, RetryableServerError),
        ],
    )
    def test_http_status_mapping(self, status, expected):
        with pytest.raises(expected):
            Werk24Client._raise_for_status("https://example.invalid", status)

    def test_a_quota_refusal_is_not_a_retryable_server_error(self):
        assert issubclass(InsufficientCreditsException, ServerException)
        assert not issubclass(InsufficientCreditsException, RetryableServerError)

    async def test_a_refused_key_at_connect_is_unauthorized(self):
        client = Werk24Client(token="t", region="r")
        refused = InvalidStatus(Response(403, "Forbidden", Headers()))
        with patch.object(
            client, "_create_websocket_session", AsyncMock(side_effect=refused)
        ):
            with pytest.raises(ApiKeyRejectedException) as caught:
                await client._connect_with_retry()
        assert isinstance(caught.value, UnauthorizedException)

    def test_the_legacy_classes_stay_importable(self):
        from werk24 import (  # noqa: F401
            W24AuthenticationError,
            W24RateLimitError,
            W24ServerError,
            W24ValidationError,
        )
