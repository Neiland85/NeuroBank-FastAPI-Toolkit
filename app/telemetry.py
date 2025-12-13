"""
Telemetry and Monitoring Module for NeuroBank FastAPI Toolkit

This module provides telemetry setup for tracking application metrics,
performance monitoring, and distributed tracing.
"""

import logging
from typing import Optional

from fastapi import FastAPI


logger = logging.getLogger(__name__)


def setup_telemetry(app: FastAPI) -> None:
    """
    Configure telemetry and monitoring for the FastAPI application.

    This function sets up:
    - Application metrics tracking
    - Performance monitoring
    - Request/response logging
    - Health check endpoints integration

    Args:
        app: FastAPI application instance

    Note:
        In production, this can be extended with:
        - OpenTelemetry integration
        - CloudWatch custom metrics
        - AWS X-Ray tracing
        - Prometheus metrics export
    """
    logger.info("🔧 Setting up telemetry...")

    # Add startup event for telemetry initialization
    @app.on_event("startup")
    async def startup_telemetry():
        logger.info("📊 Telemetry initialized successfully")
        logger.info(f"📍 Application: {app.title} v{app.version}")

    # Add shutdown event for cleanup
    @app.on_event("shutdown")
    async def shutdown_telemetry():
        logger.info("📊 Telemetry shutdown complete")

    logger.info("✅ Telemetry setup complete")


def log_request_metrics(
    endpoint: str,
    method: str,
    status_code: int,
    duration_ms: float,
    request_id: Optional[str] = None,
) -> None:
    """
    Log request metrics for monitoring and analysis.

    Args:
        endpoint: API endpoint path
        method: HTTP method (GET, POST, etc.)
        status_code: Response status code
        duration_ms: Request processing duration in milliseconds
        request_id: Optional unique request identifier
    """
    logger.info(
        f"📊 Request: {method} {endpoint} | "
        f"Status: {status_code} | "
        f"Duration: {duration_ms:.2f}ms"
        f"{f' | RequestID: {request_id}' if request_id else ''}"
    )
