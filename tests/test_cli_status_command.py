import pytest
from typer.testing import CliRunner

from werk24 import SystemStatus
from werk24.cli.commands import status as status_cmd


async def mock_get_status():
    return SystemStatus(
        page="Werk24",
        status_indicator="ok",
        status_description="All systems operational",
        incidents=[],
        scheduled_maintenances=[],
        components=[],
    )


@pytest.mark.filterwarnings("ignore::ResourceWarning")
def test_status_cli(monkeypatch):
    """Test the status CLI command.

    Note: ResourceWarning is suppressed because asyncio.run() (used in the CLI command)
    creates and properly closes an event loop, but pytest's garbage collector timing
    can trigger a false positive warning. The event loop is correctly managed by
    asyncio.run() - this is a known pytest + asyncio.run() interaction issue.
    See: https://github.com/pytest-dev/pytest/issues/5502
    """
    monkeypatch.setattr(status_cmd.Werk24Client, "get_system_status", mock_get_status)
    runner = CliRunner()
    result = runner.invoke(status_cmd.app, [])
    assert result.exit_code == 0
    assert '"status_indicator": "ok"' in result.stdout
