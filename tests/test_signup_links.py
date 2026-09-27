"""Where ``werk24 init``, the README and the package metadata send a new user.

A developer without an API key is pointed at the Werk24 API signup page, the
console page where API keys are created, and the free browser demo. Each URL
is printed on one line, so a copy from a narrow terminal still works, and no
file a user reads promises a free trial.

These tests run offline and need no credentials.
"""

import io
import re
from pathlib import Path

import pytest
from rich.console import Console
from typer.testing import CliRunner

import werk24.cli.commands.init as init_cmd
from werk24.utils.defaults import API_KEYS_URL, DEMO_URL, Settings
from werk24.utils.exceptions import InvalidLicenseException

ROOT = Path(__file__).resolve().parents[1]

EXPECTED_SIGNUP = (
    "https://studio.werk24.io/console/signup?product=console&plan=payg"
    "&utm_source=werk24-python&utm_medium=cli&utm_campaign=init"
)

TRIAL = re.compile(r"\btrial\b", re.I)


def test_signup_url_default_is_the_console_signup(monkeypatch):
    monkeypatch.delenv("SIGNUP_URL", raising=False)
    signup_url = str(Settings().signup_url)
    assert signup_url == EXPECTED_SIGNUP
    assert "trial" not in signup_url


def test_signup_url_env_override_still_works(monkeypatch):
    monkeypatch.setenv("SIGNUP_URL", "https://example.com/signup")
    assert str(Settings().signup_url) == "https://example.com/signup"


@pytest.fixture
def run_init(monkeypatch):
    """Run ``werk24 init`` on a machine without a key.

    Returns a function that takes the terminal input and returns the Typer
    result, what the Rich console printed (80 columns wide, no colour) and
    the licenses that would have been saved. Nothing is written to disk.
    """
    monkeypatch.delenv("SIGNUP_URL", raising=False)

    def no_key():
        raise InvalidLicenseException("none")

    saved = []

    def save(license, path=None):
        saved.append(license)
        return "/nowhere/.werk24"

    buf = io.StringIO()
    monkeypatch.setattr(init_cmd, "locate_license", no_key)
    monkeypatch.setattr(init_cmd, "save_license_file", save)
    monkeypatch.setattr(init_cmd, "settings", Settings())
    monkeypatch.setattr(
        init_cmd,
        "console",
        Console(file=buf, width=80, color_system=None, force_terminal=False),
    )

    def run(answers: str):
        result = CliRunner().invoke(init_cmd.app, [], input=answers)
        return result, buf.getvalue(), saved

    return run


def test_init_sign_up_prints_signup_keys_and_demo_on_single_lines(run_init):
    result, out, saved = run_init("2\nsome-token\n\n")

    assert result.exit_code == 0, out + result.stdout
    lines = out.splitlines()
    # Whole-line membership at 80 columns: a URL Rich folded across two lines
    # would not match, and would not work when copied.
    assert EXPECTED_SIGNUP in lines
    assert API_KEYS_URL in lines
    assert DEMO_URL in lines
    assert saved[0].token == "some-token"
    assert not TRIAL.search(out + result.stdout)


def test_init_sign_up_prints_an_overridden_url_as_text(run_init, monkeypatch):
    monkeypatch.setattr(
        init_cmd, "settings", Settings(signup_url="https://example.com/[bold]x")
    )
    result, out, _ = run_init("2\nsome-token\n\n")

    assert result.exit_code == 0, out + result.stdout
    assert "https://example.com/[bold]x" in out.splitlines()


def test_init_menu_offers_api_key_and_signup(run_init):
    result, out, saved = run_init("1\nsome-token\n\n")

    assert result.exit_code == 0, out + result.stdout
    assert "Paste an API key" in out
    assert "Sign up for the Werk24 API" in out
    assert not TRIAL.search(out + result.stdout)
    assert saved[0].token == "some-token"


@pytest.mark.parametrize(
    "name",
    [
        "README.md",
        "pyproject.toml",
        "werk24/utils/defaults.py",
        "werk24/cli/commands/init.py",
    ],
)
def test_no_trial_promise_in_user_facing_files(name):
    # \b keeps words such as "industrial" from matching.
    text = (ROOT / name).read_text(encoding="utf-8")
    assert not TRIAL.search(text), name


def test_package_and_readme_links():
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")

    assert 'documentation = "https://v2.docs.werk24.io"' in pyproject
    assert "https://studio.werk24.io/console/signup" in pyproject
    assert "werk24.io/docs" not in pyproject
    assert "werk24.io/docs" not in readme
    assert "https://studio.werk24.io/console/signup" in readme
    assert "https://studio.werk24.io/console/keys" in readme
    assert "W24TECHREAD_AUTH_TOKEN" in readme
