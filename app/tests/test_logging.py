"""Tests for logging module."""

import logging
import os
from unittest.mock import patch

import pytest

from app.utils.logging import get_logger, setup_logging


class TestSetupLogging:
    """Tests for setup_logging function."""

    def test_setup_logging_configures_root_logger(self):
        """Test that setup_logging configures the root logger."""
        setup_logging()
        root = logging.getLogger()
        assert root.level in (
            logging.DEBUG,
            logging.INFO,
            logging.WARNING,
            logging.ERROR,
        )

    def test_setup_logging_default_level(self):
        """Test setup_logging with default INFO level."""
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("LOG_LEVEL", None)
            setup_logging()
            root = logging.getLogger()
            assert root.level == logging.INFO

    def test_setup_logging_debug_level(self):
        """Test setup_logging with DEBUG level."""
        with patch.dict(os.environ, {"LOG_LEVEL": "DEBUG"}, clear=False):
            setup_logging()
            root = logging.getLogger()
            assert root.level == logging.DEBUG

    def test_setup_logging_warning_level(self):
        """Test setup_logging with WARNING level."""
        with patch.dict(os.environ, {"LOG_LEVEL": "WARNING"}, clear=False):
            setup_logging()
            root = logging.getLogger()
            assert root.level == logging.WARNING

    def test_setup_logging_invalid_level_defaults_to_info(self):
        """Test setup_logging with invalid level defaults to INFO."""
        with patch.dict(os.environ, {"LOG_LEVEL": "INVALID"}, clear=False):
            setup_logging()
            root = logging.getLogger()
            assert root.level == logging.INFO

    def test_setup_logging_adds_handler(self):
        """Test that setup_logging adds at least one handler."""
        setup_logging()
        root = logging.getLogger()
        assert len(root.handlers) >= 1


class TestGetLogger:
    """Tests for get_logger function."""

    def test_get_logger_returns_logger(self):
        """Test that get_logger returns a logger instance."""
        logger = get_logger("test_module")
        assert isinstance(logger, logging.Logger)
        assert logger.name == "test_module"

    def test_get_logger_different_names(self):
        """Test that get_logger returns different loggers for different names."""
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")
        assert logger1.name != logger2.name

    def test_get_logger_same_name_returns_same_logger(self):
        """Test that get_logger returns same logger for same name."""
        logger1 = get_logger("same_module")
        logger2 = get_logger("same_module")
        assert logger1 is logger2
