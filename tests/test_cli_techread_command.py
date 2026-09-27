"""Offline tests for ``werk24 techread``.

The client is replaced by a stand-in whose ``read_drawing`` yields a fixed
list of messages, so the hook dispatch, the JSON output, the stderr report
and the exit status are exercised without credentials or a network.

ResourceWarning is suppressed on each test for the same reason as in
tests/test_cli_status_command.py: the command runs asyncio.run(), and
pytest's garbage collector timing can report the closed event loop.
"""

import json
import re
import sys
import uuid
from pathlib import Path

import pytest
import typer
from typer.testing import CliRunner

import werk24.cli.werk24 as werk24_cli
from werk24.cli.commands import techread
from werk24.models import (
    AskDocumentProfile,
    AskPageAssessment,
    AskRedaction,
    AskType,
    TechreadMessage,
)
from werk24.models.v2.responses import ResponseMetaDataComponentDrawing
from werk24.techread import Werk24Client
from werk24.utils.exceptions import UserInputError

README = Path(__file__).resolve().parent.parent / "README.md"

pytestmark = pytest.mark.filterwarnings("ignore::ResourceWarning")


class FakeClient(Werk24Client):
    """A client that yields ``messages`` instead of reading anything."""

    messages: list = []
    asks: list = []

    def __init__(self, *args, **kwargs):
        # No license lookup and no connection.
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        return False

    async def read_drawing(self, drawing, asks, max_pages=5, **kwargs):
        FakeClient.asks = list(asks)
        for message in FakeClient.messages:
            yield message


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setattr(techread, "Werk24Client", FakeClient)
    FakeClient.messages = []
    FakeClient.asks = []
    return FakeClient


@pytest.fixture
def drawing(tmp_path):
    path = tmp_path / "d.pdf"
    path.write_bytes(b"%PDF-1.4\n")
    return str(path)


def msg(type_, subtype, payload=None, exceptions=(), **kw):
    return TechreadMessage.model_validate(
        {
            "request_id": str(uuid.uuid4()),
            "message_type": type_,
            "message_subtype": subtype,
            "payload_dict": payload,
            "exceptions": list(exceptions),
            **kw,
        }
    )


def exc(level, type_, **kw):
    return {"exception_level": level, "exception_type": type_, **kw}


COMPLETED = msg("PROGRESS", "COMPLETED")


def invoke(*args):
    return CliRunner().invoke(techread.app, list(args))


def _command_params():
    return typer.main.get_command(techread.app).params


def _ask_opts():
    return {
        opt
        for param in _command_params()
        for opt in param.opts
        if opt.startswith("--ask-")
    }


def test_every_ask_type_has_a_flag():
    opts = _ask_opts()
    for ask_type in AskType:
        flag = "--ask-" + ask_type.value.lower().replace("_", "-")
        assert flag in opts, f"{ask_type} has no {flag} option"


def test_readme_documents_exactly_the_ask_flags():
    text = README.read_text(encoding="utf-8")
    assert set(re.findall(r"--ask-[a-z-]+", text)) == _ask_opts()

    all_opts = {
        opt
        for param in _command_params()
        for opt in list(param.opts) + list(param.secondary_opts)
    }
    example_lines = [line for line in text.splitlines() if "werk24 techread" in line]
    assert example_lines
    for line in example_lines:
        for token in re.findall(r"--[a-z][a-z-]*", line):
            assert token in all_opts, f"README uses {token}, which is not an option"


def test_new_ask_flags_send_their_asks(client, drawing):
    client.messages = [COMPLETED]
    result = invoke(
        drawing, "--ask-redaction", "--ask-document-profile", "--ask-page-assessment"
    )
    assert result.exit_code == 0, result.output
    assert {type(ask) for ask in client.asks} == {
        AskRedaction,
        AskDocumentProfile,
        AskPageAssessment,
    }


def test_answer_prints_one_json_object_that_round_trips(client, drawing):
    client.messages = [
        msg("PROGRESS", "INITIALIZATION_SUCCESS"),
        msg(
            "ASK",
            "META_DATA",
            ResponseMetaDataComponentDrawing().model_dump(mode="json"),
        ),
        COMPLETED,
    ]
    result = invoke(drawing, "--ask-meta-data")
    assert result.exit_code == 0, result.output

    lines = result.stdout.splitlines()
    assert len(lines) == 1
    parsed = TechreadMessage.model_validate_json(lines[0])
    assert isinstance(parsed.payload_dict, ResponseMetaDataComponentDrawing)
    assert "payload_bytes" not in json.loads(lines[0])
    assert "Received message" not in result.output
    assert "<class" not in result.output
    assert result.stderr == ""


def test_failed_ask_exits_1_and_reports_on_stderr(client, drawing):
    client.messages = [
        msg(
            "ASK",
            "META_DATA",
            exceptions=[exc("ERROR", "DRAWING_FILE_FORMAT_UNSUPPORTED")],
        ),
        COMPLETED,
    ]
    result = invoke(drawing, "--ask-meta-data")
    assert result.exit_code == 1

    obj = json.loads(result.stdout)
    assert obj["exceptions"][0]["exception_type"] == "DRAWING_FILE_FORMAT_UNSUPPORTED"
    assert "ERROR: DRAWING_FILE_FORMAT_UNSUPPORTED on META_DATA (page 0)" in (
        result.stderr
    )


def test_unknown_exception_type_still_fails(client, drawing):
    client.messages = [
        msg(
            "ASK",
            "META_DATA",
            exceptions=[exc("ERROR", "SOMETHING_NEW", reason="x")],
        ),
        COMPLETED,
    ]
    result = invoke(drawing, "--ask-meta-data")
    assert result.exit_code == 1
    assert "ERROR: SOMETHING_NEW on META_DATA (page 0, reason x)" in result.stderr


def test_warning_keeps_exit_0(client, drawing):
    client.messages = [
        msg("ASK", "META_DATA"),
        msg("PROGRESS", "COMPLETED", exceptions=[exc("WARNING", "READ_INCOMPLETE")]),
    ]
    result = invoke(drawing, "--ask-meta-data")
    assert result.exit_code == 0, result.output
    assert "WARNING: READ_INCOMPLETE on COMPLETED (page 0)" in result.stderr


def test_read_without_completion_exits_1(client, drawing):
    client.messages = [msg("ASK", "META_DATA")]
    result = invoke(drawing, "--ask-meta-data")
    assert result.exit_code == 1
    assert "before the server reported it complete" in result.stderr


def test_server_error_message_exits_1(client, drawing):
    client.messages = [msg("ERROR", "INTERNAL")]
    result = invoke(drawing, "--ask-meta-data")
    assert result.exit_code == 1
    assert result.stdout == ""
    assert "ERROR: the server reported INTERNAL (page 0)" in result.stderr


def test_pretty_output_is_indented_json(client, drawing):
    client.messages = [msg("ASK", "META_DATA"), COMPLETED]
    result = invoke(drawing, "--ask-meta-data", "--pretty")
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["message_subtype"] == "META_DATA"
    assert "\n  " in result.stdout


def test_binary_payload_is_left_out(client, drawing):
    redaction = msg(
        "ASK",
        "REDACTION",
        {"ask_version": "v2", "ask_type": "REDACTION", "redaction_zones": []},
        payload_url="https://example.com/r.pdf",
    )
    redaction.payload_bytes = b"\xff\xfe"
    client.messages = [redaction, COMPLETED]

    result = invoke(drawing, "--ask-redaction")
    assert result.exit_code == 0, result.output
    obj = json.loads(result.stdout)
    assert obj["payload_url"] == "https://example.com/r.pdf"
    assert "payload_bytes" not in obj


def test_non_ascii_is_written_as_utf8(client, drawing):
    client.messages = [
        msg(
            "ASK",
            "CUSTOM",
            {
                "ask_version": "v2",
                "ask_type": "CUSTOM",
                "custom_id": "c",
                "output": "Ø6 H7",
            },
        ),
        COMPLETED,
    ]
    result = invoke(drawing, "--ask-custom", "c")
    assert result.exit_code == 0, result.output
    assert "Ø6 H7".encode("utf-8") in result.stdout_bytes


def test_no_ask_selected(client, drawing):
    result = invoke(drawing)
    assert result.exit_code == 1
    assert isinstance(result.exception, UserInputError)
    assert "--ask-meta-data" in str(result.exception)


def test_error_panel_goes_to_stderr(client, drawing, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["werk24", "techread", drawing])
    with pytest.raises(SystemExit) as exit_info:
        werk24_cli.main()
    assert exit_info.value.code == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "Invalid Input" in captured.err
