"""
Logging configuration module.

This module configures structured JSON logging for the application.
It reads configuration internally to avoid circular dependencies.
"""

import logging
import os
import sys

from pythonjsonlogger import jsonlogger


def setup_logging():
    """
    Configure application logging system with NO parameters.

    Reads configuration from environment variables internally to avoid
    circular import dependencies with app.config module.

    This function MUST be called with zero arguments to satisfy CodeQL
    and maintain architectural boundaries.
    """
    # Read log level from environment, default to INFO
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    # Validate log level
    numeric_level = getattr(logging, log_level, logging.INFO)

    # Create JSON formatter
    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(name)s %(levelname)s %(message)s"
    )

    # Configure handler for stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Clear existing handlers to avoid duplicates
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    # Configure uvicorn logger
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.setLevel(numeric_level)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger for the specified module."""
    return logging.getLogger(name)
