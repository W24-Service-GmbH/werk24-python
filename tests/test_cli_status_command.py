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


def test_status_cli(monkeypatch):
    monkeypatch.setattr(status_cmd.Werk24Client, "get_system_status", mock_get_status)
    runner = CliRunner()
    result = runner.invoke(status_cmd.app, [])
    assert result.exit_code == 0
    assert '"status_indicator": "ok"' in result.stdout
