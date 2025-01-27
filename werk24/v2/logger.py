import logging
from enum import Enum
from typing import Optional

LOGGER_NAME = "werk24"


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


def get_logger(
    log_level: Optional[LogLevel] = None,
    log_format: str = "%(asctime)s - %(name)s [%(levelname)s] %(message)s",
) -> logging.Logger:
    """
    Configures and returns a logger with the specified log level and format.

    Args:
    ----
    - log_level (LogLevel): The log level to set for the logger. Default is LogLevel.INFO.
    - log_format (str): The format string for the logger. Default format includes timestamp, name, and level.

    Returns:
    -------
    - logging.Logger: A configured logger instance.
    """
    logger = logging.getLogger(LOGGER_NAME)
    if not logger.hasHandlers():  # Avoid duplicate handlers
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(log_format))
        logger.addHandler(handler)

        if log_level is not None:
            logger.setLevel(log_level.value)  # Use LogLevel directly
    return logger
