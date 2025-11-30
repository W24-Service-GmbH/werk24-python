"""
Tests for WebSocket connection management features.

This module tests:
- Auto-reconnect on disconnect
- Graceful shutdown
- Configuration options
"""

from unittest.mock import patch

import pytest

from werk24.techread import Werk24Client


@pytest.fixture
def client():
    """Create a Werk24Client instance with test configuration."""
    return Werk24Client(
        token="test_token",
        region="eu-central-1",  # Required for license validation
        ping_interval=0.1,  # Fast ping for testing
        ping_timeout=0.05,  # Short timeout for testing
        max_reconnect_attempts=3,
        reconnect_delay=0.1,
    )


@pytest.mark.asyncio
async def test_ping_interval_configured(client):
    """Test that ping_interval is properly configured."""
    assert client._ping_interval == 0.1
    assert client._ping_timeout == 0.05


@pytest.mark.asyncio
async def test_max_reconnect_attempts_configured(client):
    """Test that max_reconnect_attempts is properly configured."""
    assert client._max_reconnect_attempts == 3
    assert client._reconnect_delay == 0.1


@pytest.mark.asyncio
async def test_no_reconnect_during_shutdown(client):
    """Test that reconnect is skipped during shutdown."""
    client._is_shutting_down = True

    with patch.object(client, "_connect_with_retry") as mock_connect:
        await client._reconnect()

        # Should not attempt to connect during shutdown
        mock_connect.assert_not_called()


@pytest.mark.asyncio
async def test_shutdown_flag(client):
    """Test that shutdown flag prevents reconnection."""
    client._is_shutting_down = True

    # Reconnect should do nothing when shutting down
    await client._reconnect()

    # No exception should be raised
    assert client._is_shutting_down
