"""Tests for telemetry module."""

import logging
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI

from app.telemetry import log_request_metrics, setup_telemetry


class TestSetupTelemetry:
    """Tests for setup_telemetry function."""

    def test_setup_telemetry_adds_events(self):
        """Test that setup_telemetry configures app events."""
        app = FastAPI(title="Test App", version="1.0.0")
        setup_telemetry(app)
        # Verify startup and shutdown events were added
        assert len(app.router.on_startup) > 0
        assert len(app.router.on_shutdown) > 0

    def test_setup_telemetry_logs_info(self, caplog):
        """Test that setup_telemetry logs setup messages."""
        app = FastAPI(title="Test App", version="1.0.0")
        with caplog.at_level(logging.INFO):
            setup_telemetry(app)
        assert "Setting up telemetry" in caplog.text
        assert "Telemetry setup complete" in caplog.text


class TestLogRequestMetrics:
    """Tests for log_request_metrics function."""

    def test_log_request_metrics_basic(self, caplog):
        """Test basic request metrics logging."""
        with caplog.at_level(logging.INFO):
            log_request_metrics(
                endpoint="/api/test",
                method="GET",
                status_code=200,
                duration_ms=15.5,
            )
        assert "GET" in caplog.text
        assert "/api/test" in caplog.text

    def test_log_request_metrics_with_request_id(self, caplog):
        """Test request metrics logging with request ID."""
        with caplog.at_level(logging.INFO):
            log_request_metrics(
                endpoint="/api/users",
                method="POST",
                status_code=201,
                duration_ms=25.3,
                request_id="req-123-abc",
            )
        assert "POST" in caplog.text
        assert "/api/users" in caplog.text

    def test_log_request_metrics_error_status(self, caplog):
        """Test request metrics logging with error status code."""
        with caplog.at_level(logging.INFO):
            log_request_metrics(
                endpoint="/api/error",
                method="GET",
                status_code=500,
                duration_ms=100.0,
            )
        assert "500" in caplog.text or "GET" in caplog.text
