"""``werk24 health-check`` has to report a rejected token, and fail on it.

It used to print "License Status: Found" for any token it could read, put a
refused connection under Network Information, and exit 0 whatever happened.
Now the License panel says which token was found, where it came from and
whether the API accepted it, and the command exits 1 when no token is found,
the token is rejected or the connection fails. The System Status panel stays
informational.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from rich.console import Console
from typer.testing import CliRunner
from websockets.datastructures import Headers
from websockets.exceptions import InvalidStatus
from websockets.http11 import Response

import werk24.utils.license as license_module
from werk24 import SystemStatus
from werk24.cli.commands import health_check
from werk24.techread import Werk24Client
from werk24.utils.exceptions import API_TOKENS_URL, ServerException
from werk24.utils.license import TOKEN_ENV_KEY

TOKEN = "wk24_abcdefghijklmnopWXYZ"
OTHER_TOKEN = "wk24_zyxwvutsrqponmlkABCD"

pytestmark = pytest.mark.filterwarnings("ignore::ResourceWarning")


async def _status_ok():
    return SystemStatus(
        page="Werk24",
        status_indicator="ok",
        status_description="All systems operational",
        incidents=[],
        scheduled_maintenances=[],
        components=[],
    )


async def _status_fails():
    raise ServerException("status page unreachable")


def _refuse_403(*args, **kwargs):
    raise InvalidStatus(Response(403, "Forbidden", Headers(), b""))


@pytest.fixture
def license_file(tmp_path, monkeypatch):
    """Only this path is searched, and the variable starts unset."""
    path = tmp_path / ".werk24"
    monkeypatch.setattr(license_module, "SEARCH_PATHS", [str(path)])
    monkeypatch.delenv(TOKEN_ENV_KEY, raising=False)
    monkeypatch.setattr(license_module, "_SHADOW_WARNED", set())
    monkeypatch.setattr(health_check, "console", Console(width=240))
    monkeypatch.setattr(Werk24Client, "get_system_status", _status_ok)
    return path


def _run():
    return CliRunner().invoke(health_check.app, [])


def test_no_key_fails_without_connecting(license_file):
    connect = AsyncMock()
    with patch.object(Werk24Client, "_connect_with_retry", connect):
        result = _run()

    assert result.exit_code == 1
    assert "Not Found" in result.stdout
    assert "Skipped: no API token found" in result.stdout
    connect.assert_not_called()


def test_a_rejected_key_is_named_and_fails(license_file, monkeypatch):
    monkeypatch.setenv(TOKEN_ENV_KEY, TOKEN)
    with patch.object(
        Werk24Client, "_create_websocket_session", side_effect=_refuse_403
    ):
        result = _run()

    out = result.stdout
    assert result.exit_code == 1
    assert "License Status" in out
    assert "Found" in out
    assert "ending in WXYZ" in out
    assert "W24TECHREAD_AUTH_TOKEN environment variable" in out
    assert "Rejected by the Werk24 API" in out
    assert "Refused: API token rejected" in out
    assert "API Token Rejected" in out
    assert API_TOKENS_URL in out
    assert TOKEN not in out


def test_an_accepted_key_passes(license_file, monkeypatch):
    monkeypatch.setenv(TOKEN_ENV_KEY, TOKEN)
    with patch.multiple(
        Werk24Client,
        _connect_with_retry=AsyncMock(),
        _graceful_shutdown=AsyncMock(),
    ):
        result = _run()

    assert result.exit_code == 0
    assert "Successful" in result.stdout
    assert "Accepted" in result.stdout
    assert "API Token Rejected" not in result.stdout


def test_a_failed_connection_fails_and_leaves_the_key_unchecked(
    license_file, monkeypatch
):
    monkeypatch.setenv(TOKEN_ENV_KEY, TOKEN)
    with patch.object(
        Werk24Client,
        "_connect_with_retry",
        AsyncMock(side_effect=ServerException("boom")),
    ):
        result = _run()

    assert result.exit_code == 1
    assert "Not checked" in result.stdout
    assert "boom" in result.stdout
    assert "API Token Rejected" not in result.stdout


def test_the_status_panel_is_informational(license_file, monkeypatch):
    monkeypatch.setenv(TOKEN_ENV_KEY, TOKEN)
    monkeypatch.setattr(Werk24Client, "get_system_status", _status_fails)
    with patch.multiple(
        Werk24Client,
        _connect_with_retry=AsyncMock(),
        _graceful_shutdown=AsyncMock(),
    ):
        result = _run()

    assert result.exit_code == 0
    assert "status page unreachable" in result.stdout


def test_a_file_hiding_the_variable_is_noted(license_file, monkeypatch):
    license_file.write_text(f"{TOKEN}\n")
    monkeypatch.setenv(TOKEN_ENV_KEY, OTHER_TOKEN)
    with patch.multiple(
        Werk24Client,
        _connect_with_retry=AsyncMock(),
        _graceful_shutdown=AsyncMock(),
    ):
        result = _run()

    out = result.stdout
    assert result.exit_code == 0
    assert "Note" in out
    assert "W24TECHREAD_AUTH_TOKEN is also set, to a different token" in out
    assert f"the file {license_file}" in out
    assert "ending in WXYZ" in out
    assert TOKEN not in out
    assert OTHER_TOKEN not in out
