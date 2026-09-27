"""Where ``werk24 init`` saves the API key, and what a missing key says.

``werk24 init`` used to save the key to ``.werk24`` in whatever folder it ran
in, so a script started from any other folder found no key and was told its
license "is invalid or has expired". It also saved the shortened key a key
list shows, which can never work, and it would not replace an existing key.

Now init saves to ``~/.werk24``, which every client version reads from any
folder, says where it saved the key, and asks before replacing one. A
missing key raises LicenseNotFoundException, whose message lists every place
the client looked. A value that cannot be a key is refused before anything
is sent.
"""

from __future__ import annotations

import io
import os
import pickle
import secrets
import subprocess
import sys
import uuid
from pathlib import Path

import pytest
from rich.console import Console
from typer.testing import CliRunner

import werk24.cli.werk24 as cli_main
import werk24.utils.license as license_module
from werk24 import SystemStatus
from werk24.cli.commands import health_check
from werk24.cli.commands import init as init_cmd
from werk24.techread import Werk24Client
from werk24.utils.exceptions import (
    API_KEYS_URL,
    InvalidLicenseException,
    LicenseNotFoundException,
    TechreadException,
)
from werk24.utils.license import (
    REGION_ENV_KEY,
    TOKEN_ENV_KEY,
    License,
    find_license,
    find_license_in_envs,
    locate_license,
    parse_license_text,
    save_license_file,
    token_problem,
)

pytestmark = pytest.mark.filterwarnings("ignore::ResourceWarning")

BULLET = "•"
MIDDLE_DOT = "·"

UNUSABLE_KEYS = [
    "wk24_" + BULLET * 12 + "wxyz",
    "wk24_" + MIDDLE_DOT * 20,
    "wk24_...wxyz",
    "wk24_****wxyz",
    "Token wk24_abc",
    "wk24_abc def",
]

USABLE_KEYS = [
    "not-a-valid-token",
    str(uuid.uuid4()),
    secrets.token_hex(16),
    "a.b.c",
    "wk24_" + secrets.token_urlsafe(32),
]


class Layout:
    """The folders of one test: a home folder, a project and elsewhere."""

    def __init__(self, root: Path):
        self.home = root / "home"
        self.proj = root / "proj"
        self.sub = self.proj / "sub"
        self.elsewhere = root / "elsewhere"
        for folder in (self.home, self.proj, self.sub, self.elsewhere):
            folder.mkdir(parents=True)

    @property
    def home_key(self) -> Path:
        return self.home / ".werk24"

    @property
    def proj_key(self) -> Path:
        return self.proj / ".werk24"

    def search_paths(self) -> list[str]:
        return [
            ".werk24",
            str(self.home / ".werk24"),
            "werk24_license.txt",
            str(self.home / "werk24_license.txt"),
        ]


@pytest.fixture
def layout(tmp_path, monkeypatch) -> Layout:
    """A home folder and a project, with nothing configured anywhere."""
    folders = Layout(tmp_path)
    monkeypatch.setattr(license_module, "SEARCH_PATHS", folders.search_paths())
    monkeypatch.setattr(license_module, "USER_LICENSE_PATH", str(folders.home_key))
    monkeypatch.setattr(license_module, "_SHADOW_WARNED", set())
    monkeypatch.delenv(TOKEN_ENV_KEY, raising=False)
    monkeypatch.delenv(REGION_ENV_KEY, raising=False)
    monkeypatch.chdir(folders.proj)
    return folders


@pytest.fixture
def captured(monkeypatch) -> io.StringIO:
    """What the init and health-check commands print through rich."""
    buffer = io.StringIO()
    console = Console(file=buffer, width=500, color_system=None)
    monkeypatch.setattr(init_cmd, "console", console)
    monkeypatch.setattr(health_check, "console", console)
    return buffer


def _init(captured: io.StringIO, answers: str):
    """Run ``werk24 init`` with these answers on stdin.

    Returns:
        tuple: The result and everything printed, prompts included.
    """
    result = CliRunner().invoke(init_cmd.app, [], input=answers)
    return result, captured.getvalue() + result.output


class TestSaving:
    def test_the_key_is_saved_in_the_home_folder(self, layout):
        saved = save_license_file(License(token="k"))

        assert saved == os.path.abspath(str(layout.home_key))
        assert layout.home_key.exists()
        assert not layout.proj_key.exists()
        if os.name == "posix":
            assert os.stat(layout.home_key).st_mode & 0o777 == 0o600

    def test_an_explicit_path_is_honoured(self, layout):
        target = layout.elsewhere / "key.txt"
        saved = save_license_file(License(token="k"), path=str(target))

        assert saved == os.path.abspath(str(target))
        assert target.read_text() == f"{TOKEN_ENV_KEY}=k\n"
        assert not layout.home_key.exists()

    def test_an_unresolvable_home_folder_is_refused(self, layout, monkeypatch):
        monkeypatch.setattr(license_module, "USER_LICENSE_PATH", "~/.werk24")
        with pytest.raises(InvalidLicenseException) as excinfo:
            save_license_file(License(token="k"))
        assert TOKEN_ENV_KEY in excinfo.value.reason
        assert not (layout.proj / "~").exists()


class TestInit:
    def test_a_key_saved_in_a_project_is_found_from_any_folder(
        self, layout, captured, monkeypatch
    ):
        result, out = _init(captured, "1\nwk24_abcDEF123\n\n")

        assert result.exit_code == 0, out
        assert layout.home_key.exists()
        assert not layout.proj_key.exists()
        assert os.path.abspath(str(layout.home_key)) in out

        monkeypatch.chdir(layout.elsewhere)
        lookup = locate_license()
        assert lookup.license.token == "wk24_abcDEF123"
        assert lookup.source == "file"
        assert lookup.path == os.path.abspath(str(layout.home_key))

    def test_three_shortened_keys_save_nothing(self, layout, captured):
        masked = "wk24_" + BULLET * 12 + "wxyz"
        result, out = _init(captured, "1\n" + f"{masked}\n\n" * 3)

        assert result.exit_code == 1
        assert not layout.home_key.exists()
        assert not layout.proj_key.exists()
        assert "shortened" in out
        assert "Maximum number of attempts reached" in out

    def test_a_refused_paste_can_be_followed_by_a_good_one(self, layout, captured):
        result, out = _init(captured, "1\nToken wk24_abc\n\nwk24_abc\n\n")

        assert result.exit_code == 0, out
        assert "That key cannot be used: it contains spaces" in out
        assert layout.home_key.read_text() == f"{TOKEN_ENV_KEY}=wk24_abc\n"

    def test_an_existing_key_is_kept_on_no(self, layout, captured):
        layout.home_key.write_text("old_key\n")

        result, out = _init(captured, "n\n")

        assert result.exit_code == 0, out
        assert layout.home_key.read_text() == "old_key\n"
        assert "Kept the existing key" in out
        assert os.path.abspath(str(layout.home_key)) in out

    def test_an_existing_key_is_kept_when_there_is_no_answer(self, layout, captured):
        layout.home_key.write_text("old_key\n")

        result, out = _init(captured, "")

        assert result.exit_code == 0, out
        assert layout.home_key.read_text() == "old_key\n"
        assert "Kept the existing key" in out

    def test_an_existing_key_is_replaced_on_yes(self, layout, captured):
        layout.home_key.write_text("old_key\n")

        result, out = _init(captured, "y\n1\nnew_key\n\n")

        assert result.exit_code == 0, out
        assert layout.home_key.read_text() == f"{TOKEN_ENV_KEY}=new_key\n"

    def test_a_key_in_the_project_folder_is_named_and_left_alone(
        self, layout, captured
    ):
        layout.proj_key.write_text("old_key\n")

        result, out = _init(captured, "y\n1\nnew_key\n\n")

        assert result.exit_code == 0, out
        assert layout.home_key.read_text() == f"{TOKEN_ENV_KEY}=new_key\n"
        assert layout.proj_key.read_text() == "old_key\n"
        proj_path = os.path.abspath(str(layout.proj_key))
        assert f"In this folder the key is still read from the file {proj_path}" in out

    def test_a_key_from_the_environment_says_a_saved_key_would_win(
        self, layout, captured, monkeypatch
    ):
        monkeypatch.setenv(TOKEN_ENV_KEY, "env_key")

        result, out = _init(captured, "n\n")

        assert result.exit_code == 0, out
        assert "W24TECHREAD_AUTH_TOKEN environment variable" in out
        assert "would be used instead of the variable's key" in out
        assert not layout.home_key.exists()


class TestNoKeyFound:
    def test_the_message_lists_where_the_client_looked(self, layout):
        with pytest.raises(LicenseNotFoundException) as excinfo:
            locate_license()

        exc = excinfo.value
        text = str(exc)
        assert isinstance(exc, InvalidLicenseException)
        assert TOKEN_ENV_KEY in text
        for path in license_module.SEARCH_PATHS:
            assert os.path.abspath(path) in text
        assert "werk24 init" in text
        assert f"It is saved to {os.path.abspath(str(layout.home_key))}" in text
        assert API_KEYS_URL in text
        assert "invalid or has expired" not in text
        assert "Details:" not in text
        assert exc.reason == "no API key was found"

    def test_find_license_raises_the_same_class(self, layout):
        with pytest.raises(LicenseNotFoundException):
            find_license()

    def test_the_constructor_error_is_the_same_class(self, layout):
        with pytest.raises(LicenseNotFoundException):
            Werk24Client(region="r")

    def test_it_survives_a_pickle_round_trip(self, layout):
        with pytest.raises(LicenseNotFoundException) as excinfo:
            locate_license()

        copy = pickle.loads(pickle.dumps(excinfo.value))
        assert type(copy) is LicenseNotFoundException
        assert str(copy) == str(excinfo.value)
        assert copy.searched == excinfo.value.searched
        assert copy.save_path == excinfo.value.save_path

    def test_it_builds_without_arguments(self):
        exc = LicenseNotFoundException()
        assert exc.searched == []
        assert "werk24 init" in str(exc)
        assert API_KEYS_URL in str(exc)

    def test_it_is_exported_from_the_package(self):
        from werk24 import LicenseNotFoundException as exported

        assert exported is LicenseNotFoundException

    def test_an_unusable_file_is_listed_with_the_reason(self, layout):
        layout.proj_key.write_text("wk24_" + BULLET * 12 + "wxyz\n")

        with pytest.raises(LicenseNotFoundException) as excinfo:
            locate_license()

        path = os.path.abspath(str(layout.proj_key))
        assert (
            f"{path}: found, but not usable: it looks like the shortened key"
            in str(excinfo.value)
        )

    def test_an_unusable_variable_is_listed_and_not_leaked(self, layout, monkeypatch):
        masked = "wk24_" + BULLET * 12 + "wxyz"
        monkeypatch.setenv(TOKEN_ENV_KEY, masked)

        assert find_license_in_envs() is None
        with pytest.raises(LicenseNotFoundException) as excinfo:
            locate_license()

        text = str(excinfo.value)
        assert (
            f"environment variable {TOKEN_ENV_KEY}: set, but not usable: "
            "it looks like the shortened key" in text
        )
        assert masked not in text


class TestCompatibility:
    def test_a_legacy_dotenv_file_in_the_project_is_found(self, layout):
        layout.proj_key.write_text(
            f"{TOKEN_ENV_KEY}=legacy_token\n{REGION_ENV_KEY}=eu-central-1\n"
        )
        lookup = locate_license()
        assert lookup.license == License(token="legacy_token", region="eu-central-1")
        assert lookup.path == os.path.abspath(str(layout.proj_key))

    def test_a_legacy_license_txt_in_the_home_folder_is_found(self, layout):
        (layout.home / "werk24_license.txt").write_text("legacy_token\n")
        assert find_license() == License(token="legacy_token")

    def test_the_project_key_wins_over_the_home_key(self, layout):
        layout.proj_key.write_text("proj_key\n")
        layout.home_key.write_text("home_key\n")
        assert find_license().token == "proj_key"

    def test_a_key_file_is_read_before_the_environment_variable(
        self, layout, monkeypatch
    ):
        # The search order is unchanged: files first, then the variable.
        layout.proj_key.write_text(f"{TOKEN_ENV_KEY}=file_key\n")
        monkeypatch.setenv(TOKEN_ENV_KEY, "env_key")

        lookup = locate_license()

        assert lookup.license.token == "file_key"
        assert lookup.source == "file"
        assert lookup.env_shadowed is True

    def test_a_file_saved_with_a_byte_order_mark_is_read(self, layout):
        layout.proj_key.write_bytes(b"\xef\xbb\xbfwk24_abc\n")
        assert find_license().token == "wk24_abc"

    def test_the_save_path_is_the_home_file_every_release_reads(self):
        # Checked in a fresh interpreter: this suite points USER_LICENSE_PATH
        # at a temporary folder in every test.
        code = (
            "import os, werk24.utils.license as m;"
            "assert m.USER_LICENSE_PATH == os.path.expanduser('~/.werk24');"
            "assert m.USER_LICENSE_PATH in m.SEARCH_PATHS;"
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


class TestUnusableKeys:
    @pytest.mark.parametrize("value", UNUSABLE_KEYS)
    def test_the_paste_is_refused_with_a_reason(self, value):
        with pytest.raises(InvalidLicenseException) as excinfo:
            parse_license_text(f"{value}\n")
        assert excinfo.value.reason
        assert value not in str(excinfo.value)

    @pytest.mark.parametrize("value", UNUSABLE_KEYS)
    def test_the_model_refuses_it(self, value):
        with pytest.raises(ValueError):
            License(token=value)

    @pytest.mark.parametrize("value", UNUSABLE_KEYS)
    def test_the_client_refuses_it_before_sending(self, value):
        with pytest.raises(InvalidLicenseException) as excinfo:
            Werk24Client(token=value, region="r")
        assert "The token passed to Werk24Client is not usable" in str(excinfo.value)

    @pytest.mark.parametrize("value", UNUSABLE_KEYS)
    def test_a_dotenv_file_holding_it_is_refused(self, value):
        with pytest.raises(InvalidLicenseException):
            parse_license_text(f"{TOKEN_ENV_KEY}={value}\n")

    @pytest.mark.parametrize("value", USABLE_KEYS)
    def test_ordinary_keys_are_accepted(self, value):
        assert token_problem(value) is None
        assert parse_license_text(f"{value}\n").token == value
        assert License(token=value).token == value

    def test_non_ascii_is_refused(self):
        assert token_problem("wk24_abcé") == (
            "it contains characters that never appear in an API key"
        )

    def test_an_empty_token_argument_is_refused(self):
        with pytest.raises(InvalidLicenseException) as excinfo:
            Werk24Client(token="  ", region="r")
        assert "it is empty" in str(excinfo.value)

    def test_a_dotenv_block_without_a_token_says_so(self):
        with pytest.raises(InvalidLicenseException) as excinfo:
            parse_license_text(f"{TOKEN_ENV_KEY}=\n")
        assert excinfo.value.reason == f"it has no value for {TOKEN_ENV_KEY}"

    def test_a_reason_survives_a_pickle_round_trip(self):
        exc = InvalidLicenseException("it is empty")
        copy = pickle.loads(pickle.dumps(exc))
        assert copy.reason == "it is empty"
        assert str(copy) == str(exc)


async def _status_ok():
    return SystemStatus(
        page="Werk24",
        status_indicator="ok",
        status_description="All systems operational",
        incidents=[],
        scheduled_maintenances=[],
        components=[],
    )


class TestHealthCheck:
    def test_no_key_lists_where_the_client_looked(
        self, layout, captured, monkeypatch
    ):
        monkeypatch.setattr(Werk24Client, "get_system_status", _status_ok)

        result = CliRunner().invoke(health_check.app, [])

        out = captured.getvalue()
        assert result.exit_code == 1
        for path in license_module.SEARCH_PATHS:
            assert os.path.abspath(path) in out
        assert f"environment variable {TOKEN_ENV_KEY}" in out
        assert API_KEYS_URL in out

    def test_a_saved_key_shows_where_it_is_read_from(
        self, layout, captured, monkeypatch
    ):
        layout.home_key.write_text("wk24_abcdefghijklmnopWXYZ\n")

        health_check.license_information(
            locate_license(), health_check.ConnectionCheck("connected")
        )

        out = captured.getvalue()
        assert "Source" in out
        assert os.path.abspath(str(layout.home_key)) in out


class TestErrorPanel:
    @pytest.mark.parametrize("text", ["[x]", "[/x]"])
    def test_brackets_in_a_message_are_printed_as_is(self, monkeypatch, text):
        class Bracketed(TechreadException):
            cli_message_header = "Bracketed"
            cli_message_body = f"a path with {text} in it"

        def raise_it():
            raise Bracketed()

        buffer = io.StringIO()
        monkeypatch.setattr(
            cli_main, "console", Console(file=buffer, width=500, color_system=None)
        )
        monkeypatch.setattr(cli_main, "app", raise_it)

        with pytest.raises(SystemExit) as excinfo:
            cli_main.main()

        assert excinfo.value.code == 1
        assert f"a path with {text} in it" in buffer.getvalue()
