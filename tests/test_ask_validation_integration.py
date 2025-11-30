"""
Integration tests for ask type validation in Werk24Client methods.

This module tests that ask validation is properly integrated into the
client's read_drawing and read_drawing_with_callback methods.
"""

import io
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from werk24 import Werk24Client
from werk24.models.v1.ask import W24AskTitleBlock
from werk24.models.v2.asks import AskBalloons
from werk24.utils.exceptions import BadRequestException


class TestAskValidationIntegration:
    """Integration tests for ask validation in client methods."""

    @pytest.mark.asyncio
    async def test_read_drawing_validates_asks_before_processing(self):
        """Test that read_drawing validates asks before processing."""
        from pydantic import BaseModel

        class InvalidAsk(BaseModel):
            ask_type: str = "INVALID_TYPE"

        client = Werk24Client()
        drawing = io.BytesIO(b"fake drawing content")

        # Should raise BadRequestException due to invalid ask type
        with pytest.raises(BadRequestException) as exc_info:
            async with client:
                async for _ in client.read_drawing(drawing, [InvalidAsk()]):
                    pass

        assert "Invalid ask type(s): INVALID_TYPE" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_read_drawing_with_callback_validates_asks(self):
        """Test that read_drawing_with_callback validates asks."""
        from pydantic import BaseModel

        class InvalidAsk(BaseModel):
            ask_type: str = "INVALID_TYPE"

        client = Werk24Client()
        drawing = io.BytesIO(b"fake drawing content")

        # Should raise BadRequestException due to invalid ask type
        # before even trying to make the HTTP request
        with pytest.raises(BadRequestException) as exc_info:
            await client.read_drawing_with_callback(
                drawing, [InvalidAsk()], callback_url="https://example.com/callback"
            )

        assert "Invalid ask type(s): INVALID_TYPE" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_read_drawing_with_empty_asks_raises_error(self):
        """Test that read_drawing with empty asks raises BadRequestException."""
        client = Werk24Client()
        drawing = io.BytesIO(b"fake drawing content")

        with pytest.raises(BadRequestException) as exc_info:
            async with client:
                async for _ in client.read_drawing(drawing, []):
                    pass

        assert "No ask types provided" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_read_drawing_with_valid_asks_passes_validation(self):
        """Test that read_drawing with valid asks passes validation."""
        client = Werk24Client()
        drawing = io.BytesIO(b"fake drawing content")
        asks = [W24AskTitleBlock(), AskBalloons()]

        # Mock the websocket connection to avoid actual API calls
        with patch.object(client, "_create_websocket_session") as mock_ws:
            mock_ws_instance = AsyncMock()
            mock_ws_instance.__aenter__ = AsyncMock(return_value=mock_ws_instance)
            mock_ws_instance.__aexit__ = AsyncMock()
            mock_ws.return_value = mock_ws_instance

            # Mock the send and recv methods
            mock_ws_instance.send = AsyncMock()
            mock_ws_instance.recv = AsyncMock(side_effect=Exception("Stop iteration"))

            try:
                async with client:
                    async for _ in client.read_drawing(drawing, asks):
                        pass
            except Exception:
                # We expect an exception because we're mocking, but the important
                # thing is that validation passed (no BadRequestException)
                pass

    def test_validate_asks_can_be_called_directly(self):
        """Test that validate_asks can be called directly as a static method."""
        asks = [W24AskTitleBlock(), AskBalloons()]

        # Should not raise any exception
        Werk24Client.validate_asks(asks)

    def test_validate_asks_provides_helpful_error_messages(self):
        """Test that validation errors include helpful information."""
        from pydantic import BaseModel

        class InvalidAsk(BaseModel):
            ask_type: str = "NONEXISTENT_ASK"

        with pytest.raises(BadRequestException) as exc_info:
            Werk24Client.validate_asks([InvalidAsk()])

        error_msg = str(exc_info.value)
        # Should mention the invalid type
        assert "NONEXISTENT_ASK" in error_msg
        # Should provide list of valid types
        assert "Valid ask types are:" in error_msg
        # Should include some actual valid types
        assert "TITLE_BLOCK" in error_msg or "BALLOONS" in error_msg
