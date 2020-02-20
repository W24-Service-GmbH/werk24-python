""" Simple integration test to verify that the connection
between the client and the W24 API is working correctly.

A successful test indicates, that
* The endpoint is correct
* The authentication was successful
* The communication was successful
"""
import asyncio
from .client import w24_client


def test_ping():
    """ Send a "ping", expect a "pong"
    """
    pong = asyncio.run(w24_client.ping())
    assert pong == "pong"


if __name__ == "__main__":
    test_ping()
