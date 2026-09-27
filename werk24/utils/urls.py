"""Werk24 web pages the client points a user to.

Plain constants with no imports, so any module can use them without adding
to what ``import werk24`` loads. ``werk24.utils.exceptions`` needs
``API_KEYS_URL`` for its messages, and the exceptions are imported by every
consumer, including those that only validate a payload against the models.
``werk24.utils.defaults`` re-exports both names, where they were first
defined.
"""

API_KEYS_URL = "https://studio.werk24.io/console/keys"
"""Werk24 console page where a signed-up customer creates and manages API keys."""

DEMO_URL = "https://studio.werk24.io/demo?utm_source=werk24-python&utm_medium=cli&utm_campaign=init"
"""Free browser demo: read a drawing without an API key."""
