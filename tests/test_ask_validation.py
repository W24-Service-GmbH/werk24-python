"""
Tests for ask type validation in Werk24Client.

This module tests the validate_asks() method to ensure it properly validates
both W24AskType (v1) and AskType (v2) ask types.
"""

import pytest

from werk24 import Werk24Client
from werk24.models.v1.ask import (
    W24AskTitleBlock,
    W24AskVariantGDTs,
    W24AskVariantMeasures,
)
from werk24.models.v2.asks import AskBalloons, AskFeatures, AskInsights
from werk24.utils.exceptions import BadRequestException


class TestAskValidation:
    """Test suite for ask type validation."""

    def test_validate_asks_with_valid_v1_asks(self):
        """Test that valid v1 ask types pass validation."""
        asks = [
            W24AskTitleBlock(),
            W24AskVariantMeasures(),
            W24AskVariantGDTs(),
        ]
        # Should not raise any exception
        Werk24Client.validate_asks(asks)

    def test_validate_asks_with_valid_v2_asks(self):
        """Test that valid v2 ask types pass validation."""
        asks = [
            AskBalloons(),
            AskFeatures(),
            AskInsights(),
        ]
        # Should not raise any exception
        Werk24Client.validate_asks(asks)

    def test_validate_asks_with_mixed_v1_and_v2_asks(self):
        """Test that mixed v1 and v2 ask types pass validation."""
        asks = [
            W24AskTitleBlock(),
            AskBalloons(),
            W24AskVariantMeasures(),
            AskFeatures(),
        ]
        # Should not raise any exception
        Werk24Client.validate_asks(asks)

    def test_validate_asks_with_empty_list(self):
        """Test that empty ask list raises BadRequestException."""
        with pytest.raises(BadRequestException) as exc_info:
            Werk24Client.validate_asks([])

        assert "No ask types provided" in str(exc_info.value)

    def test_validate_asks_with_invalid_ask_type(self):
        """Test that invalid ask type raises BadRequestException with helpful message."""
        from pydantic import BaseModel

        class InvalidAsk(BaseModel):
            ask_type: str = "INVALID_ASK_TYPE"

        with pytest.raises(BadRequestException) as exc_info:
            Werk24Client.validate_asks([InvalidAsk()])

        error_msg = str(exc_info.value)
        assert "Invalid ask type(s): INVALID_ASK_TYPE" in error_msg
        assert "Valid ask types are:" in error_msg

    def test_validate_asks_with_multiple_invalid_ask_types(self):
        """Test that multiple invalid ask types are all reported."""
        from pydantic import BaseModel

        class InvalidAsk1(BaseModel):
            ask_type: str = "INVALID_TYPE_1"

        class InvalidAsk2(BaseModel):
            ask_type: str = "INVALID_TYPE_2"

        with pytest.raises(BadRequestException) as exc_info:
            Werk24Client.validate_asks([InvalidAsk1(), InvalidAsk2()])

        error_msg = str(exc_info.value)
        assert "INVALID_TYPE_1" in error_msg
        assert "INVALID_TYPE_2" in error_msg

    def test_validate_asks_with_missing_ask_type_attribute(self):
        """Test that ask without ask_type attribute raises BadRequestException."""
        from pydantic import BaseModel

        class AskWithoutType(BaseModel):
            some_field: str = "value"

        with pytest.raises(BadRequestException) as exc_info:
            Werk24Client.validate_asks([AskWithoutType()])

        error_msg = str(exc_info.value)
        assert "(missing ask_type)" in error_msg

    def test_validate_asks_error_message_includes_valid_types(self):
        """Test that error message includes list of valid ask types."""
        from pydantic import BaseModel

        class InvalidAsk(BaseModel):
            ask_type: str = "INVALID"

        with pytest.raises(BadRequestException) as exc_info:
            Werk24Client.validate_asks([InvalidAsk()])

        error_msg = str(exc_info.value)
        # Check that some known valid types are in the error message
        assert "TITLE_BLOCK" in error_msg or "BALLOONS" in error_msg
        assert "VARIANT_MEASURES" in error_msg or "FEATURES" in error_msg
