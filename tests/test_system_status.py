from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from werk24 import SystemStatus, Werk24Client


@pytest.mark.asyncio
async def test_get_system_status():
    payload = {
        "page": "Werk24",
        "status_indicator": "ok",
        "status_description": "All systems operational",
        "incidents": [],
        "scheduled_maintenances": [],
        "components": [],
    }

    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json.return_value = payload

    mock_context = MagicMock()
    mock_context.__aenter__ = AsyncMock(return_value=mock_response)
    mock_context.__aexit__ = AsyncMock(return_value=None)

    mock_session = MagicMock()
    mock_session.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session.__aexit__ = AsyncMock(return_value=None)
    mock_session.get = MagicMock(return_value=mock_context)

    with patch.object(aiohttp, "ClientSession", return_value=mock_session):
        status = await Werk24Client.get_system_status()

    assert isinstance(status, SystemStatus)
    assert status.status_indicator == "ok"
    mock_session.get.assert_called_once()
