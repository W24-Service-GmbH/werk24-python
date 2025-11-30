"""
Example demonstrating ask type validation in werk24-python client.

This example shows how the client validates ask types before sending
requests to the API, providing helpful error messages for invalid asks.
"""

import asyncio

from werk24 import Werk24Client
from werk24.models.v1.ask import W24AskTitleBlock, W24AskVariantMeasures
from werk24.models.v2.asks import AskBalloons, AskFeatures
from werk24.utils.exceptions import BadRequestException


async def example_valid_asks():
    """Example with valid ask types (both v1 and v2)."""
    print("=" * 60)
    print("Example 1: Valid ask types")
    print("=" * 60)

    # Create a list of valid asks (mixing v1 and v2)
    asks = [
        W24AskTitleBlock(),
        W24AskVariantMeasures(),
        AskBalloons(),
        AskFeatures(),
    ]

    # Validate asks before sending (this is done automatically by read_drawing)
    try:
        Werk24Client.validate_asks(asks)
        print("✓ All ask types are valid!")
        print(f"  - {len(asks)} asks validated successfully")
    except BadRequestException as e:
        print(f"✗ Validation failed: {e}")

    print()


async def example_invalid_ask():
    """Example with an invalid ask type."""
    print("=" * 60)
    print("Example 2: Invalid ask type")
    print("=" * 60)

    from pydantic import BaseModel

    # Create an invalid ask type
    class InvalidAsk(BaseModel):
        ask_type: str = "NONEXISTENT_ASK_TYPE"

    asks = [
        W24AskTitleBlock(),
        InvalidAsk(),  # This will fail validation
    ]

    try:
        Werk24Client.validate_asks(asks)
        print("✓ All ask types are valid!")
    except BadRequestException as e:
        print(f"✗ Validation failed:")
        print(f"  {e}")

    print()


async def example_empty_asks():
    """Example with empty ask list."""
    print("=" * 60)
    print("Example 3: Empty ask list")
    print("=" * 60)

    asks = []

    try:
        Werk24Client.validate_asks(asks)
        print("✓ All ask types are valid!")
    except BadRequestException as e:
        print(f"✗ Validation failed:")
        print(f"  {e}")

    print()


async def example_validation_in_read_drawing():
    """Example showing automatic validation in read_drawing."""
    print("=" * 60)
    print("Example 4: Automatic validation in read_drawing")
    print("=" * 60)

    import io

    from pydantic import BaseModel

    class InvalidAsk(BaseModel):
        ask_type: str = "INVALID_TYPE"

    client = Werk24Client()
    drawing = io.BytesIO(b"fake drawing content")

    print("Attempting to call read_drawing with invalid ask type...")

    try:
        async with client:
            async for message in client.read_drawing(drawing, [InvalidAsk()]):
                print(f"Received message: {message}")
    except BadRequestException as e:
        print(f"✓ Validation caught the error before sending to API:")
        print(f"  {e}")
    except Exception as e:
        print(f"Other error: {e}")

    print()


async def example_helpful_error_message():
    """Example showing the helpful error message with valid ask types."""
    print("=" * 60)
    print("Example 5: Helpful error message")
    print("=" * 60)

    from pydantic import BaseModel

    class InvalidAsk1(BaseModel):
        ask_type: str = "WRONG_TYPE_1"

    class InvalidAsk2(BaseModel):
        ask_type: str = "WRONG_TYPE_2"

    asks = [InvalidAsk1(), InvalidAsk2()]

    try:
        Werk24Client.validate_asks(asks)
    except BadRequestException as e:
        error_msg = str(e)
        print("Error message includes:")
        print(f"  - Invalid ask types: WRONG_TYPE_1, WRONG_TYPE_2")
        print(f"  - List of all valid ask types")
        print()
        print("Full error message (truncated):")
        print(f"  {error_msg[:200]}...")

    print()


async def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("Ask Type Validation Examples")
    print("=" * 60 + "\n")

    await example_valid_asks()
    await example_invalid_ask()
    await example_empty_asks()
    await example_validation_in_read_drawing()
    await example_helpful_error_message()

    print("=" * 60)
    print("Examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
