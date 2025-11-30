"""Tests for the new specific exception classes.

This module tests the W24AuthenticationError, W24ValidationError,
W24RateLimitError, and W24ServerError exception classes to ensure
they properly handle error details and provide useful information.
"""

import pytest

from werk24.utils.exceptions import (
    W24AuthenticationError,
    W24RateLimitError,
    W24ServerError,
    W24ValidationError,
)


class TestW24AuthenticationError:
    """Tests for W24AuthenticationError exception class."""

    def test_basic_initialization(self):
        """Test basic initialization with default values."""
        error = W24AuthenticationError()
        assert error.error_code == "401"
        assert error.error_details == {}
        assert error.request_id is None
        assert "Authentication with the Werk24 API failed" in error.cli_message_body

    def test_initialization_with_details(self):
        """Test initialization with custom details."""
        error = W24AuthenticationError(
            details="Invalid token provided",
            error_code="401",
            error_details={"reason": "token_expired"},
            request_id="test-request-123",
        )
        assert error.error_code == "401"
        assert error.error_details == {"reason": "token_expired"}
        assert error.request_id == "test-request-123"
        assert "Invalid token provided" in str(error)

    def test_inheritance(self):
        """Test that W24AuthenticationError inherits from TechreadException."""
        error = W24AuthenticationError()
        from werk24.utils.exceptions import TechreadException

        assert isinstance(error, TechreadException)


class TestW24ValidationError:
    """Tests for W24ValidationError exception class."""

    def test_basic_initialization(self):
        """Test basic initialization with default values."""
        error = W24ValidationError()
        assert error.error_code == "400"
        assert error.error_details == {}
        assert error.request_id is None
        assert "The request failed validation" in error.cli_message_body

    def test_initialization_with_invalid_asks(self):
        """Test initialization with invalid ask types."""
        error = W24ValidationError(
            details="Invalid ask types specified",
            error_details={
                "invalid_asks": ["INVALID_ASK_1", "INVALID_ASK_2"],
                "valid_asks": ["VARIANT_MEASURES", "VARIANT_GDTS", "TITLE_BLOCK"],
            },
            request_id="test-request-456",
        )
        assert error.error_code == "400"
        assert "INVALID_ASK_1" in str(error)
        assert "VARIANT_MEASURES" in str(error)
        assert error.request_id == "test-request-456"

    def test_initialization_with_field_error(self):
        """Test initialization with field-specific error."""
        error = W24ValidationError(
            details="Field validation failed",
            error_details={"field": "asks", "error": "must not be empty"},
        )
        assert "Field 'asks'" in str(error)
        assert "must not be empty" in str(error)

    def test_initialization_with_many_valid_asks(self):
        """Test that long lists of valid asks are truncated."""
        valid_asks = [f"ASK_{i}" for i in range(20)]
        error = W24ValidationError(
            error_details={"invalid_asks": ["BAD_ASK"], "valid_asks": valid_asks}
        )
        # Should show first 5 and ellipsis
        assert "..." in str(error)

    def test_inheritance(self):
        """Test that W24ValidationError inherits from TechreadException."""
        error = W24ValidationError()
        from werk24.utils.exceptions import TechreadException

        assert isinstance(error, TechreadException)


class TestW24RateLimitError:
    """Tests for W24RateLimitError exception class."""

    def test_basic_initialization(self):
        """Test basic initialization with default values."""
        error = W24RateLimitError()
        assert error.error_code == "429"
        assert error.error_details == {}
        assert error.request_id is None
        assert error.retry_after is None
        assert "You have exceeded the API rate limit" in error.cli_message_body

    def test_initialization_with_retry_after(self):
        """Test initialization with retry_after parameter."""
        error = W24RateLimitError(
            details="Rate limit exceeded",
            retry_after=60,
            error_details={"limit": 1000, "current": 1000},
            request_id="test-request-789",
        )
        assert error.retry_after == 60
        assert "60 seconds" in str(error)
        assert "1000/1000" in str(error)
        assert error.request_id == "test-request-789"

    def test_initialization_with_retry_after_in_details(self):
        """Test that retry_after is extracted from error_details."""
        error = W24RateLimitError(
            error_details={"retry_after": 120, "limit": 500, "current": 500}
        )
        assert error.retry_after == 120
        assert "120 seconds" in str(error)

    def test_retry_after_parameter_takes_precedence(self):
        """Test that explicit retry_after parameter takes precedence."""
        error = W24RateLimitError(retry_after=30, error_details={"retry_after": 60})
        assert error.retry_after == 30

    def test_inheritance(self):
        """Test that W24RateLimitError inherits from TechreadException."""
        error = W24RateLimitError()
        from werk24.utils.exceptions import TechreadException

        assert isinstance(error, TechreadException)


class TestW24ServerError:
    """Tests for W24ServerError exception class."""

    def test_basic_initialization(self):
        """Test basic initialization with default values."""
        error = W24ServerError()
        assert error.error_code == "500"
        assert error.error_details == {}
        assert error.request_id is None
        assert error.is_transient is False
        assert "The Werk24 API encountered an error" in error.cli_message_body

    def test_initialization_with_500_error(self):
        """Test initialization with 500 Internal Server Error."""
        error = W24ServerError(
            details="Internal server error occurred",
            error_code="500",
            error_details={"error_type": "database_connection"},
            request_id="test-request-abc",
        )
        assert error.error_code == "500"
        assert error.is_transient is False
        assert "test-request-abc" in str(error)

    def test_initialization_with_503_error(self):
        """Test initialization with 503 Service Unavailable."""
        error = W24ServerError(
            details="Service temporarily unavailable",
            error_code="503",
            error_details={"retry_after": 30},
            request_id="test-request-def",
        )
        assert error.error_code == "503"
        assert error.is_transient is True
        assert "temporarily unavailable" in str(error)
        assert "30 seconds" in str(error)

    def test_is_transient_flag(self):
        """Test that is_transient flag can be set explicitly."""
        error = W24ServerError(error_code="500", is_transient=True)
        assert error.is_transient is True

    def test_request_id_in_message(self):
        """Test that request_id is included in the error message."""
        error = W24ServerError(request_id="unique-request-id-123")
        assert "unique-request-id-123" in str(error)

    def test_inheritance(self):
        """Test that W24ServerError inherits from TechreadException."""
        error = W24ServerError()
        from werk24.utils.exceptions import TechreadException

        assert isinstance(error, TechreadException)


class TestExceptionAttributes:
    """Tests for common attributes across all new exception classes."""

    def test_all_exceptions_have_error_code(self):
        """Test that all new exceptions have error_code attribute."""
        exceptions = [
            W24AuthenticationError(),
            W24ValidationError(),
            W24RateLimitError(),
            W24ServerError(),
        ]
        for exc in exceptions:
            assert hasattr(exc, "error_code")
            assert isinstance(exc.error_code, str)

    def test_all_exceptions_have_error_details(self):
        """Test that all new exceptions have error_details attribute."""
        exceptions = [
            W24AuthenticationError(),
            W24ValidationError(),
            W24RateLimitError(),
            W24ServerError(),
        ]
        for exc in exceptions:
            assert hasattr(exc, "error_details")
            assert isinstance(exc.error_details, dict)

    def test_all_exceptions_have_request_id(self):
        """Test that all new exceptions have request_id attribute."""
        exceptions = [
            W24AuthenticationError(),
            W24ValidationError(),
            W24RateLimitError(),
            W24ServerError(),
        ]
        for exc in exceptions:
            assert hasattr(exc, "request_id")

    def test_all_exceptions_have_cli_message_header(self):
        """Test that all new exceptions have cli_message_header attribute."""
        exceptions = [
            W24AuthenticationError(),
            W24ValidationError(),
            W24RateLimitError(),
            W24ServerError(),
        ]
        for exc in exceptions:
            assert hasattr(exc, "cli_message_header")
            assert isinstance(exc.cli_message_header, str)
            assert len(exc.cli_message_header) > 0

    def test_all_exceptions_have_cli_message_body(self):
        """Test that all new exceptions have cli_message_body attribute."""
        exceptions = [
            W24AuthenticationError(),
            W24ValidationError(),
            W24RateLimitError(),
            W24ServerError(),
        ]
        for exc in exceptions:
            assert hasattr(exc, "cli_message_body")
            assert isinstance(exc.cli_message_body, str)
            assert len(exc.cli_message_body) > 0
