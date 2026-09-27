"""``werk24 techread`` with the image options, with and without Pillow.

``--ask-sheet-images`` and ``--ask-view-images`` show what they receive with
Pillow, which werk24 does not install unless the ``images`` extra is asked
for. A missing Pillow used to raise at the first image, which ended the read
and dropped every result after it. These tests hold the behaviour that
replaced that: a read that asks for anything else runs to the end and warns
once, a read that asks only for images stops before it starts, and every
message names the extra to install.

No test here needs Pillow. Its presence and absence are both simulated
through ``sys.modules``, so the suite behaves the same whether or not the
machine running it has Pillow installed.

ResourceWarning is suppressed for the reason tests/test_cli_techread_command.py
gives: the command runs asyncio.run().
"""

import json
import pickle
import sys
import types
import uuid
from pathlib import Path

import pytest
from typer.testing import CliRunner

from werk24.cli import werk24 as cli_main
from werk24.cli.commands import techread as techread_cmd
from werk24.models import (
    AskType,
    TechreadMessage,
    TechreadMessageSubtype,
    TechreadMessageType,
)
from werk24.techread import Werk24Client
from werk24.utils.exceptions import (
    OptionalDependencyMissingError,
    TechreadException,
    UserInputError,
)

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

pytestmark = pytest.mark.filterwarnings("ignore::ResourceWarning")

INSTALL_COMMAND = 'pip install "werk24[images]"'
REQUEST_ID = uuid.uuid4()


def _image(subtype=AskType.SHEET_IMAGES, page=0, data=b"\x89PNG\r\n\x1a\n"):
    return TechreadMessage(
        request_id=REQUEST_ID,
        message_type=TechreadMessageType.ASK,
        message_subtype=subtype,
        page_number=page,
        payload_bytes=data,
    )


def _meta_data():
    return TechreadMessage(
        request_id=REQUEST_ID,
        message_type=TechreadMessageType.ASK,
        message_subtype=AskType.META_DATA,
        payload_dict={"marker": "meta-data-was-printed"},
    )


def _completed():
    return TechreadMessage(
        request_id=REQUEST_ID,
        message_type=TechreadMessageType.PROGRESS,
        message_subtype=TechreadMessageSubtype.PROGRESS_COMPLETED,
    )


class _StubClient(Werk24Client):
    """The real client, with the connection and the server replaced.

    ``call_hooks_for_message`` is the real one, so a hook that raises ends
    the read exactly as it would against the server.
    """

    messages: list = []
    constructed = 0

    def __init__(self, *args, **kwargs):
        type(self).constructed += 1
        super().__init__(token="t", region="r")

    async def __aenter__(self):
        return self

    async def __aexit__(self, *exc_info):
        return False

    async def read_drawing(self, drawing, asks, **kwargs):
        for message in self.messages:
            yield message


@pytest.fixture
def stub_client(monkeypatch):
    # A subclass per test, so the counter and the messages do not leak.
    class Stub(_StubClient):
        messages = []
        constructed = 0

    monkeypatch.setattr(techread_cmd, "Werk24Client", Stub)
    return Stub


@pytest.fixture
def drawing(tmp_path) -> Path:
    path = tmp_path / "drawing.pdf"
    path.write_bytes(b"%PDF-1.4\n")
    return path


@pytest.fixture
def no_pillow(monkeypatch):
    """Make ``from PIL import Image`` raise ImportError."""
    monkeypatch.setitem(sys.modules, "PIL", None)
    monkeypatch.setitem(sys.modules, "PIL.Image", None)


@pytest.fixture
def fake_pillow(monkeypatch):
    """Install a stand-in ``PIL.Image`` that records what it was asked to show."""
    shown = []

    class FakeImage:
        def show(self, title=None):
            shown.append(title)

    image_module = types.ModuleType("PIL.Image")
    image_module.open = lambda fp: FakeImage()
    image_module.shown = shown
    pil = types.ModuleType("PIL")
    pil.Image = image_module
    monkeypatch.setitem(sys.modules, "PIL", pil)
    monkeypatch.setitem(sys.modules, "PIL.Image", image_module)
    return image_module


def _invoke(drawing, *flags):
    return CliRunner().invoke(cli_main.app, ["techread", str(drawing), *flags])


class TestWithoutPillow:
    def test_the_read_runs_to_the_end_and_prints_the_other_results(
        self, no_pillow, stub_client, drawing
    ):
        stub_client.messages = [
            _image(page=0),
            _image(page=1),
            _meta_data(),
            _completed(),
        ]
        result = _invoke(drawing, "--ask-sheet-images", "--ask-meta-data")
        assert result.exit_code == 0, result.output
        assert result.exception is None
        assert "meta-data-was-printed" in result.output
        # Each image still gets its JSON line; only showing it is skipped.
        subtypes = [
            json.loads(line)["message_subtype"] for line in result.stdout.splitlines()
        ]
        assert subtypes == ["SHEET_IMAGES", "SHEET_IMAGES", "META_DATA"]

    def test_the_warning_names_the_extra_once(self, no_pillow, stub_client, drawing):
        stub_client.messages = [
            _image(page=0),
            _image(page=1),
            _meta_data(),
            _completed(),
        ]
        result = _invoke(drawing, "--ask-sheet-images", "--ask-meta-data")
        assert result.output.count(INSTALL_COMMAND) == 1
        assert INSTALL_COMMAND in result.stderr
        assert "Invalid Input" not in result.output

    def test_only_image_asks_stop_before_the_read_starts(
        self, no_pillow, stub_client, drawing
    ):
        result = _invoke(drawing, "--ask-sheet-images", "--ask-view-images")
        assert isinstance(result.exception, OptionalDependencyMissingError)
        assert result.exit_code == 1
        assert stub_client.constructed == 0

    def test_the_error_panel_shows_the_extra(
        self, no_pillow, stub_client, drawing, monkeypatch, capsys
    ):
        """rich reads ``[images]`` as markup unless it is escaped."""
        monkeypatch.setattr(
            sys, "argv", ["werk24", "techread", str(drawing), "--ask-sheet-images"]
        )
        with pytest.raises(SystemExit) as exit_info:
            cli_main.main()
        assert exit_info.value.code == 1
        captured = capsys.readouterr()
        assert captured.out == ""
        assert "Optional Dependency Missing" in captured.err
        assert "werk24[images]" in captured.err


class TestWithPillow:
    def test_each_image_is_shown(self, fake_pillow, stub_client, drawing):
        stub_client.messages = [
            _image(page=0),
            _image(AskType.VIEW_IMAGES, page=1),
            _meta_data(),
            _completed(),
        ]
        result = _invoke(
            drawing, "--ask-sheet-images", "--ask-view-images", "--ask-meta-data"
        )
        assert result.exit_code == 0, result.output
        assert fake_pillow.shown == ["SHEET_IMAGES, page 1", "VIEW_IMAGES, page 2"]
        assert INSTALL_COMMAND not in result.output

    def test_an_image_that_cannot_be_shown_is_a_warning(
        self, fake_pillow, stub_client, drawing
    ):
        def refuse(fp):
            raise OSError("no display")

        fake_pillow.open = refuse
        stub_client.messages = [_image(), _meta_data(), _completed()]
        result = _invoke(drawing, "--ask-sheet-images", "--ask-meta-data")
        assert result.exit_code == 0, result.output
        assert "no display" in result.stderr
        assert "meta-data-was-printed" in result.stdout

    def test_an_image_message_without_data_is_skipped(
        self, fake_pillow, stub_client, drawing
    ):
        stub_client.messages = [_image(data=None), _meta_data(), _completed()]
        result = _invoke(drawing, "--ask-sheet-images", "--ask-meta-data")
        assert result.exit_code == 0, result.output
        assert fake_pillow.shown == []
        assert "meta-data-was-printed" in result.stdout


class TestTheError:
    def test_it_is_still_a_user_input_error(self):
        error = OptionalDependencyMissingError("Pillow", "images")
        assert isinstance(error, UserInputError)
        assert isinstance(error, TechreadException)

    def test_it_names_the_install_command(self):
        error = OptionalDependencyMissingError("Pillow", "images")
        assert error.install_command == INSTALL_COMMAND
        assert INSTALL_COMMAND in error.cli_message_body

    def test_it_survives_pickling(self):
        error = OptionalDependencyMissingError("Pillow", "images", details="x")
        copy = pickle.loads(pickle.dumps(error))
        assert (copy.package, copy.extra, copy.details) == ("Pillow", "images", "x")
        assert copy.cli_message_body == error.cli_message_body


class TestTheExtra:
    @pytest.fixture
    def project(self):
        root = Path(__file__).resolve().parent.parent
        with open(root / "pyproject.toml", "rb") as fh:
            return tomllib.load(fh)["project"]

    def test_the_extra_the_cli_names_installs_pillow(self, project):
        extra = project["optional-dependencies"][techread_cmd.IMAGES_EXTRA]
        assert [spec.split(">=")[0].strip().lower() for spec in extra] == ["pillow"]

    def test_pillow_is_not_a_dependency_of_the_library(self, project):
        assert not any(
            spec.lower().startswith("pillow") for spec in project["dependencies"]
        )
