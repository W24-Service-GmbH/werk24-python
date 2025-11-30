"""
Example demonstrating WebSocket connection management features.

This example shows how to use the enhanced WebSocket connection management
features including heartbeat, auto-reconnect, and graceful shutdown.
"""

import asyncio

from werk24 import Werk24Client
from werk24.models.v2.asks import AskBalloons


async def main():
    """
    Demonstrate WebSocket connection management with custom configuration.
    """
    # Create client with custom connection management settings
    client = Werk24Client(
        token="your_token_here",
        region="eu-central-1",
        ping_interval=30.0,  # Send ping every 30 seconds (built-in websockets feature)
        ping_timeout=10.0,  # Wait 10 seconds for pong response
        max_reconnect_attempts=3,  # Try to reconnect up to 3 times
        reconnect_delay=1.0,  # Initial delay of 1 second, with exponential backoff
    )

    # The client automatically manages the WebSocket connection
    async with client:
        # Connection is established with retry logic
        # Ping/pong heartbeat is handled automatically by websockets library

        # Read a drawing - connection will auto-reconnect if it drops
        with open("path/to/drawing.pdf", "rb") as f:
            drawing_bytes = f.read()

        asks = [AskBalloons()]

        async for message in client.read_drawing(drawing_bytes, asks):
            print(f"Received: {message.message_type}")

            # If connection drops during processing, it will automatically
            # reconnect and continue receiving messages

    # When exiting the context, graceful shutdown is performed:
    # WebSocket connection is closed cleanly


async def example_with_default_settings():
    """
    Use default connection management settings.
    """
    # Default settings:
    # - ping_interval: 30.0 seconds
    # - ping_timeout: 10.0 seconds
    # - max_reconnect_attempts: 3
    # - reconnect_delay: 1.0 second (with exponential backoff)

    client = Werk24Client(
        token="your_token_here",
        region="eu-central-1",
    )

    async with client:
        # Connection management happens automatically
        pass


async def example_aggressive_reconnect():
    """
    Configure aggressive reconnection for unstable networks.
    """
    client = Werk24Client(
        token="your_token_here",
        region="eu-central-1",
        ping_interval=10.0,  # More frequent heartbeats
        ping_timeout=5.0,  # Shorter timeout
        max_reconnect_attempts=5,  # More retry attempts
        reconnect_delay=0.5,  # Faster initial retry
    )

    async with client:
        # Will reconnect more aggressively if connection drops
        pass


if __name__ == "__main__":
    # Run the main example
    asyncio.run(main())
