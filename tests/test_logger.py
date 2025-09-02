import logging

import pytest

from werk24.utils.logger import LOGGER_NAME, LogLevel, get_logger


@pytest.fixture(autouse=True)
def reset_logger():
    """Ensure a clean logger for each test."""
    get_logger.cache_clear()
    logger = logging.getLogger(LOGGER_NAME)
    logger.handlers.clear()
    yield
    logger.handlers.clear()
    get_logger.cache_clear()


def test_get_logger_returns_singleton():
    logger1 = get_logger(LogLevel.INFO)
    handlers_before = list(logger1.handlers)
    logger2 = get_logger(LogLevel.INFO)
    assert logger1 is logger2
    assert logger2.handlers == handlers_before


def test_get_logger_accepts_enum():
    logger = get_logger(LogLevel.DEBUG)
    assert logger.level == logging.DEBUG


def test_get_logger_accepts_string():
    logger = get_logger("ERROR")
    assert logger.level == logging.ERROR

