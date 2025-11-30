"""Example demonstrating the use of new specific exception classes.

This example shows how to handle different types of API errors using the
new W24AuthenticationError, W24ValidationError, W24RateLimitError, and
W24ServerError exception classes.
"""

import asyncio

from werk24 import (
    W24AuthenticationError,
    W24RateLimitError,
    W24ServerError,
    W24ValidationError,
    Werk24Client,
)


async def handle_api_errors():
    """Demonstrate error handling with specific exception types."""

    # Example 1: Authentication Error (401)
    # Note: In real usage, this would be raised by the API client
    # For demonstration, we'll create the exception directly
    print("Example 1: Authentication Error")
    error = W24AuthenticationError(
        details="Invalid token provided",
        error_code="401",
        error_details={"reason": "token_expired"},
        request_id="req-auth-123",
    )
    print(f"  Error code: {error.error_code}")
    print(f"  Details: {error.error_details}")
    print(f"  Request ID: {error.request_id}")

    # Example 2: Validation Error (400)
    # This would be raised if invalid ask types are provided
    error = W24ValidationError(
        details="Invalid ask types specified",
        error_details={
            "invalid_asks": ["INVALID_ASK"],
            "valid_asks": ["VARIANT_MEASURES", "VARIANT_GDTS", "TITLE_BLOCK"],
        },
        request_id="req-123",
    )
    print(f"\nValidation Error: {error}")

    # Example 3: Rate Limit Error (429)
    # This would be raised if rate limit is exceeded
    error = W24RateLimitError(
        details="Rate limit exceeded",
        retry_after=60,
        error_details={"limit": 1000, "current": 1000},
        request_id="req-456",
    )
    print(f"\nRate Limit Error: {error}")
    print(f"Retry after: {error.retry_after} seconds")

    # Example 4: Server Error (500)
    error = W24ServerError(
        details="Internal server error", error_code="500", request_id="req-789"
    )
    print(f"\nServer Error: {error}")
    print(f"Is transient: {error.is_transient}")

    # Example 5: Service Unavailable (503)
    error = W24ServerError(
        details="Service temporarily unavailable",
        error_code="503",
        error_details={"retry_after": 30},
        request_id="req-abc",
    )
    print(f"\nService Unavailable: {error}")
    print(f"Is transient: {error.is_transient}")


def parse_api_error_response(status_code: int, response_body: dict):
    """Parse API error response and raise appropriate exception.

    This function demonstrates how to convert API error responses
    (matching the ErrorResponse model from crew-api) into specific
    exception types.

    Args:
        status_code: HTTP status code from the API response
        response_body: Parsed JSON response body with error details

    Raises:
        W24AuthenticationError: For 401 responses
        W24ValidationError: For 400 responses
        W24RateLimitError: For 429 responses
        W24ServerError: For 500/503 responses
    """
    error_code = response_body.get("code", str(status_code))
    message = response_body.get("message", "An error occurred")
    details = response_body.get("details", {})
    request_id = response_body.get("request_id")

    if status_code == 401:
        raise W24AuthenticationError(
            details=message,
            error_code=error_code,
            error_details=details,
            request_id=request_id,
        )
    elif status_code == 400:
        raise W24ValidationError(
            details=message,
            error_code=error_code,
            error_details=details,
            request_id=request_id,
        )
    elif status_code == 429:
        retry_after = details.get("retry_after")
        raise W24RateLimitError(
            details=message,
            error_code=error_code,
            error_details=details,
            request_id=request_id,
            retry_after=retry_after,
        )
    elif status_code in (500, 503):
        raise W24ServerError(
            details=message,
            error_code=error_code,
            error_details=details,
            request_id=request_id,
            is_transient=(status_code == 503),
        )


def example_error_handling_with_retry():
    """Example showing how to implement retry logic with rate limit errors."""
    import time

    max_retries = 3
    retry_count = 0

    while retry_count < max_retries:
        try:
            # Simulate API call
            # In real code, this would be: client.read_drawing(...)

            # Simulate rate limit error
            if retry_count < 2:
                raise W24RateLimitError(
                    details="Rate limit exceeded",
                    retry_after=2,  # Short wait for demo
                    error_details={"limit": 100, "current": 100},
                )

            print("Request succeeded!")
            break

        except W24RateLimitError as e:
            retry_count += 1
            if retry_count >= max_retries:
                print(f"Max retries reached. Giving up.")
                raise

            wait_time = e.retry_after or 5
            print(
                f"Rate limited. Waiting {wait_time} seconds before retry {retry_count}/{max_retries}..."
            )
            time.sleep(wait_time)

        except W24ServerError as e:
            if e.is_transient:
                retry_count += 1
                if retry_count >= max_retries:
                    print(f"Max retries reached. Giving up.")
                    raise

                wait_time = e.error_details.get("retry_after", 5)
                print(
                    f"Service unavailable. Waiting {wait_time} seconds before retry {retry_count}/{max_retries}..."
                )
                time.sleep(wait_time)
            else:
                # Non-transient error, don't retry
                print(f"Permanent server error. Not retrying.")
                raise


if __name__ == "__main__":
    print("=== Exception Handling Examples ===\n")

    # Run async examples
    asyncio.run(handle_api_errors())

    print("\n=== Retry Logic Example ===\n")
    try:
        example_error_handling_with_retry()
    except Exception as e:
        print(f"Final error: {e}")

    print("\n=== Parsing API Error Response Example ===\n")

    # Example API error response (matches ErrorResponse model from crew-api)
    api_response = {
        "code": "400",
        "message": "Invalid ask type specified",
        "details": {
            "invalid_asks": ["INVALID_ASK"],
            "valid_asks": ["VARIANT_MEASURES", "VARIANT_GDTS", "TITLE_BLOCK"],
        },
        "request_id": "123e4567-e89b-12d3-a456-426614174000",
    }

    try:
        parse_api_error_response(400, api_response)
    except W24ValidationError as e:
        print(f"Caught validation error: {e.error_code}")
        print(f"Invalid asks: {e.error_details.get('invalid_asks')}")
        print(f"Request ID: {e.request_id}")
