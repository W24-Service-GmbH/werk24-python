"""Root pytest configuration for the werk24 test suite.

This module provides the pytest_plugins declaration that must be at the root level.
"""

# Import fixtures from the fixtures package - must be at root level conftest
pytest_plugins = [
    "tests.fixtures.clients",
]
