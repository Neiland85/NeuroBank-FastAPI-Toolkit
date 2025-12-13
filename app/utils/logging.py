"""
Logging configuration module.

Configures structured JSON logging for the application.
Reads configuration from environment variables internally to avoid
circular dependencies with app.config.
"""

import logging
import os
import sys

from pythonjsonlogger import jsonlogger


def setup_logging() -> None:
    """
    Configure application logging system.

    IMPORTANT:
    - This function MUST be called with ZERO arguments.
    - Configuration is read exclusively from environment variables.
    - Designed to satisfy CodeQL and avoid circular imports.
    """
    # Read log level from environment (default: INFO)
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    numeric_level = getattr(logging, log_level, logging.INFO)

    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(name)s %(levelname)s %(message)s"
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()

    # Prevent duplicate handlers if setup_logging is called twice
    if not root_logger.handlers:
        root_logger.addHandler(handler)

    root_logger.setLevel(numeric_level)

    # Uvicorn loggers (important in prod)
    for logger_name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logging.getLogger(logger_name).setLevel(numeric_level)


def get_logger(name: str) -> logging.Logger:
    """
    Return a logger configured by setup_logging.
    """
    return logging.getLogger(name)
