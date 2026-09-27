"""A refused API token has to say which token it was and where it came from.

When the API refuses the token (mistyped, deleted, revoked, or its account
closed or suspended), the client used to raise a plain UnauthorizedException
whose message named neither the token nor where it was read from. A license
file that silently took precedence over W24TECHREAD_AUTH_TOKEN made that
especially hard to find.

Now the refusal raises ApiTokenRejectedException, a subclass of
UnauthorizedException. It names the token by its last four characters, says
where it was read from and where tokens are managed, and never contains the
full token. Refusals that are not about the token keep their old classes.
"""

from __future__ import annotations

import logging
import os
import pickle
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest
from websockets.datastructures import Headers
from websockets.exceptions import InvalidStatus
from websockets.http11 import Response

import werk24.utils.license as license_module
from werk24.techread import Werk24Client
from werk24.utils.exceptions import (
    API_TOKENS_URL,
    ApiTokenRejectedException,
    PriorityTooHighError,
    ServerException,
    TechreadException,
    UnauthorizedException,
)
from werk24.utils.license import (
    TOKEN_ENV_KEY,
    License,
    find_license,
    locate_license,
    token_suffix,
)

from tests.test_priority_error_envelope import (
    _FakeResponse,
    _call_with_callback,
    _too_high,
)

TOKEN = "wk24_abcdefghijklmnopWXYZ"
OTHER_TOKEN = "wk24_zyxwvutsrqponmlkABCD"
SHADOW_WARNING = "is ignored because license files are read first"


@pytest.fixture
def no_license(tmp_path, monkeypatch):
    """No license file and no environment variable, whatever the machine has.

    Returns the path a test can write a license file to; it is the only path
    searched.
    """
    path = tmp_path / ".werk24"
    monkeypatch.setattr(license_module, "SEARCH_PATHS", [str(path)])
    monkeypatch.delenv(TOKEN_ENV_KEY, raising=False)
    monkeypatch.setattr(license_module, "_SHADOW_WARNED", set())
    return path


def _refuse(status: int):
    """A stand-in for ``_create_websocket_session`` that the server refuses."""

    def refuse(*args, **kwargs):
        raise InvalidStatus(Response(status, "Forbidden", Headers(), b""))

    return refuse


def _shadow_warnings(caplog) -> list:
    return [
        record
        for record in caplog.records
        if record.levelno == logging.WARNING and SHADOW_WARNING in record.getMessage()
    ]


class TestTheExceptionClass:
    def test_it_is_an_unauthorized_exception(self):
        assert issubclass(ApiTokenRejectedException, UnauthorizedException)
        assert issubclass(ApiTokenRejectedException, TechreadException)

    def test_it_is_exported_from_the_package(self):
        from werk24 import ApiTokenRejectedException as exported

        assert exported is ApiTokenRejectedException

    def test_it_builds_without_arguments_and_names_the_keys_page(self):
        exc = ApiTokenRejectedException()
        assert API_TOKENS_URL in str(exc)
        assert exc.token_suffix is None
        assert exc.token_source is None
        assert exc.status_code is None

    def test_details_stays_the_first_positional_argument(self):
        exc = ApiTokenRejectedException("x")
        assert "x" in str(exc)
        assert exc.details == "x"

    def test_the_lines_come_in_order(self):
        exc = ApiTokenRejectedException(
            "more", token_suffix="WXYZ", token_source="the token argument", status_code=403
        )
        text = str(exc)
        positions = [
            text.index("Token: ending in 'WXYZ'"),
            text.index("Read from: the token argument"),
            text.index("Server response: HTTP 403"),
            text.index("more"),
        ]
        assert positions == sorted(positions)
        assert text == exc.cli_message_body

    def test_it_survives_a_pickle_round_trip(self):
        exc = ApiTokenRejectedException(
            "details",
            token_suffix="WXYZ",
            token_source="the token argument",
            status_code=401,
        )
        copy = pickle.loads(pickle.dumps(exc))
        assert type(copy) is ApiTokenRejectedException
        assert copy.token_suffix == "WXYZ"
        assert copy.token_source == "the token argument"
        assert copy.status_code == 401
        assert str(copy) == str(exc)


class TestTokenSuffix:
    def test_a_long_token_gives_its_last_four_characters(self):
        assert token_suffix(TOKEN) == "WXYZ"

    def test_a_short_token_gives_nothing(self):
        assert token_suffix("short") is None
        assert token_suffix("abcdefghijk") is None  # 11 characters

    def test_the_boundary_is_twelve_characters(self):
        assert token_suffix("abcdefghijkl") == "ijkl"


class TestLocateLicense:
    def test_the_token_argument(self, no_license):
        lookup = locate_license(TOKEN, "r")
        assert lookup.source == "argument"
        assert lookup.path is None
        assert lookup.license == License(token=TOKEN, region="r")
        assert lookup.describe() == "the token argument"

    def test_the_environment_variable(self, no_license, monkeypatch):
        monkeypatch.setenv(TOKEN_ENV_KEY, TOKEN)
        lookup = locate_license()
        assert lookup.source == "environment"
        assert lookup.license.token == TOKEN
        assert "W24TECHREAD_AUTH_TOKEN environment variable" in lookup.describe()

    def test_a_license_file(self, no_license):
        no_license.write_text(f"{TOKEN}\n")
        lookup = locate_license()
        assert lookup.source == "file"
        assert lookup.path == os.path.abspath(str(no_license))
        assert lookup.env_shadowed is False
        assert lookup.describe() == f"the file {lookup.path}"

    def test_a_file_hiding_a_different_variable_warns_once(
        self, no_license, monkeypatch, caplog
    ):
        caplog.set_level(logging.WARNING, logger="werk24")
        no_license.write_text(f"{TOKEN}\n")
        monkeypatch.setenv(TOKEN_ENV_KEY, OTHER_TOKEN)

        first = locate_license()
        second = locate_license()

        assert first.license.token == TOKEN
        assert first.env_shadowed is True
        assert second.env_shadowed is True
        warnings = _shadow_warnings(caplog)
        assert len(warnings) == 1
        assert first.path in warnings[0].getMessage()
        assert OTHER_TOKEN not in warnings[0].getMessage()
        assert TOKEN not in warnings[0].getMessage()

    def test_a_file_and_the_same_variable_do_not_warn(
        self, no_license, monkeypatch, caplog
    ):
        caplog.set_level(logging.WARNING, logger="werk24")
        no_license.write_text(f"{TOKEN}\n")
        monkeypatch.setenv(TOKEN_ENV_KEY, f"  {TOKEN}  ")

        lookup = locate_license()

        assert lookup.env_shadowed is False
        assert _shadow_warnings(caplog) == []

    def test_find_license_still_returns_an_equal_license(self, no_license):
        no_license.write_text(f"{TOKEN}\n")
        assert find_license() == License(token=TOKEN)
        assert find_license(TOKEN, "r") == License(token=TOKEN, region="r")


class TestAReplacedFindLicense:
    """A test suite that mocks the token through ``werk24.techread.find_license``.

    Earlier releases built every client's license through that name, so
    replacing it was how a test gave a bare ``Werk24Client()`` a token. The
    client has to keep calling the replacement rather than searching for a
    token itself. ``no_license`` makes sure a search would find nothing.
    """

    def test_a_bare_client_uses_the_replacement(self, no_license):
        mocked = License(token=TOKEN)
        with patch("werk24.techread.find_license", return_value=mocked) as replaced:
            client = Werk24Client()

        assert client.license is mocked
        replaced.assert_called_once_with(None, None)

    def test_the_arguments_reach_the_replacement(self, no_license):
        mocked = License(token=TOKEN, region="r")
        with patch("werk24.techread.find_license", return_value=mocked) as replaced:
            client = Werk24Client(token=OTHER_TOKEN, region="r")

        assert client.license is mocked
        replaced.assert_called_once_with(OTHER_TOKEN, "r")

    def test_a_refusal_names_the_key_but_no_source(self, no_license):
        with patch(
            "werk24.techread.find_license", return_value=License(token=TOKEN)
        ):
            client = Werk24Client()

        exc = client._token_rejected(403, "wss://example.invalid")

        assert exc.token_suffix == "WXYZ"
        assert exc.token_source is None
        assert TOKEN not in str(exc)

    def test_without_a_replacement_the_source_is_recorded(self, no_license):
        no_license.write_text(f"{TOKEN}\n")
        client = Werk24Client()

        assert client.license == License(token=TOKEN)
        assert client._license_lookup.source == "file"
        assert client._license_lookup.path == os.path.abspath(str(no_license))

    def test_a_replacement_in_place_when_the_client_is_first_imported(self):
        # Checked in a fresh interpreter: the client module has to be imported
        # for the first time while werk24.utils.license.find_license is
        # replaced, so that werk24.techread binds the replacement.
        code = (
            "from unittest.mock import patch;"
            "import werk24.utils.license as m;"
            f"lic = m.License(token={TOKEN!r});"
            "p = patch('werk24.utils.license.find_license', return_value=lic);"
            "p.start();"
            "from werk24.techread import Werk24Client;"
            "assert Werk24Client().license is lic;"
            "p.stop();"
            "assert Werk24Client().license is lic;"
            "print('ok')"
        )
        result = subprocess.run(
            [sys.executable, "-c", code],
            cwd=str(Path(__file__).resolve().parent.parent),
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert result.stdout.strip() == "ok", result.stderr


@pytest.mark.asyncio
class TestTheConnectRefusal:
    async def test_a_403_names_the_key_and_where_it_came_from(self, no_license):
        client = Werk24Client(token=TOKEN, region="r")
        with patch.object(
            Werk24Client, "_create_websocket_session", side_effect=_refuse(403)
        ) as create:
            with pytest.raises(ApiTokenRejectedException) as excinfo:
                async with client:
                    pass

        exc = excinfo.value
        assert exc.token_suffix == "WXYZ"
        assert exc.status_code == 403
        assert "token argument" in exc.token_source
        text = str(exc)
        assert API_TOKENS_URL in text
        assert client._wss_server in text
        assert "Pass an active token as token= to Werk24Client." in text
        assert TOKEN not in text
        # A refused token is not a transient failure: it is not retried.
        assert create.call_count == 1

    async def test_existing_handlers_still_catch_it(self, no_license):
        with patch.object(
            Werk24Client, "_create_websocket_session", side_effect=_refuse(403)
        ):
            with pytest.raises(UnauthorizedException):
                async with Werk24Client(token=TOKEN, region="r"):
                    pass

    async def test_a_key_from_a_file_hiding_the_variable_says_so(
        self, no_license, monkeypatch
    ):
        no_license.write_text(f"{TOKEN}\n")
        monkeypatch.setenv(TOKEN_ENV_KEY, OTHER_TOKEN)
        # No token argument: the token has to come from the file. The fixture
        # makes the lookup independent of the machine.
        client = Werk24Client(region="r")
        with patch.object(
            Werk24Client, "_create_websocket_session", side_effect=_refuse(403)
        ):
            with pytest.raises(ApiTokenRejectedException) as excinfo:
                async with client:
                    pass

        path = os.path.abspath(str(no_license))
        text = str(excinfo.value)
        assert excinfo.value.token_source == f"the file {path}"
        assert f"Replace the token in {path}." in text
        assert "W24TECHREAD_AUTH_TOKEN is also set, to a different token" in text
        assert "is ignored" in text
        assert TOKEN not in text
        assert OTHER_TOKEN not in text

    async def test_a_key_from_the_variable_says_where_to_set_it(
        self, no_license, monkeypatch
    ):
        monkeypatch.setenv(TOKEN_ENV_KEY, TOKEN)
        client = Werk24Client(region="r")
        with patch.object(
            Werk24Client, "_create_websocket_session", side_effect=_refuse(403)
        ):
            with pytest.raises(ApiTokenRejectedException) as excinfo:
                async with client:
                    pass

        text = str(excinfo.value)
        assert "W24TECHREAD_AUTH_TOKEN environment variable" in text
        assert "Set W24TECHREAD_AUTH_TOKEN to an active token." in text
        assert TOKEN not in text

    async def test_a_short_key_is_not_shown_at_all(self, no_license):
        with patch.object(
            Werk24Client, "_create_websocket_session", side_effect=_refuse(403)
        ):
            with pytest.raises(ApiTokenRejectedException) as excinfo:
                async with Werk24Client(token="short", region="r"):
                    pass

        text = str(excinfo.value)
        assert excinfo.value.token_suffix is None
        assert "Token: ending" not in text
        assert "short" not in text

    async def test_a_reassigned_license_is_not_given_the_old_source(self, no_license):
        client = Werk24Client(token=TOKEN, region="r")
        client.license = License(token=OTHER_TOKEN)
        with patch.object(
            Werk24Client, "_create_websocket_session", side_effect=_refuse(403)
        ):
            with pytest.raises(ApiTokenRejectedException) as excinfo:
                async with client:
                    pass

        assert excinfo.value.token_suffix == "ABCD"
        assert excinfo.value.token_source is None
        assert "token argument" not in str(excinfo.value)

    async def test_a_key_revoked_mid_session_is_reported_on_reconnect(self, no_license):
        client = Werk24Client(token=TOKEN, region="r")
        with patch.object(
            Werk24Client, "_create_websocket_session", side_effect=_refuse(403)
        ):
            with pytest.raises(ApiTokenRejectedException) as excinfo:
                await client._reconnect()

        assert excinfo.value.status_code == 403

    @pytest.mark.parametrize("status", [500, 401])
    async def test_other_statuses_are_still_server_errors(self, no_license, status):
        with patch.object(
            Werk24Client, "_create_websocket_session", side_effect=_refuse(status)
        ):
            with pytest.raises(ServerException) as excinfo:
                async with Werk24Client(token=TOKEN, region="r"):
                    pass

        assert not isinstance(excinfo.value, ApiTokenRejectedException)


@pytest.mark.asyncio
class TestTheCallbackRefusal:
    async def test_a_401_is_a_rejected_key(self, no_license):
        client = Werk24Client(token=TOKEN, region="r")
        response = _FakeResponse(401, {"message": "Unauthorized"})
        with pytest.raises(ApiTokenRejectedException) as excinfo:
            await _call_with_callback(client, response, "PRIO3")

        exc = excinfo.value
        assert exc.status_code == 401
        assert exc.token_suffix == "WXYZ"
        assert "read-with-callback" in str(exc)
        assert TOKEN not in str(exc)
        assert response.released is True

    async def test_a_plain_403_is_still_only_unauthorized(self, no_license):
        client = Werk24Client(token=TOKEN, region="r")
        response = _FakeResponse(403, {"code": "403", "message": "Forbidden"})
        with pytest.raises(UnauthorizedException) as excinfo:
            await _call_with_callback(client, response, "PRIO3")

        assert type(excinfo.value) is not ApiTokenRejectedException

    async def test_a_priority_refusal_is_still_a_priority_error(self, no_license):
        client = Werk24Client(token=TOKEN, region="r")
        response = _FakeResponse(403, _too_high("PRIO2", "PRIO1"))
        with pytest.raises(PriorityTooHighError):
            await _call_with_callback(client, response, "PRIO1")


class TestPresignedUrlsAreNotKeys:
    def test_a_403_from_storage_is_plain_unauthorized(self):
        """An expired presigned URL is not a problem with the API token."""
        with pytest.raises(UnauthorizedException) as excinfo:
            Werk24Client._raise_for_status("https://bucket.example/x", 403)

        assert type(excinfo.value) is UnauthorizedException
