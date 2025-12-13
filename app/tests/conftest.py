"""
Pytest configuration and fixtures.

This file sets up test environment variables for local testing.
In CI, variables are set via GitHub Actions workflow.
"""

import os


def pytest_configure(config):
    """Configure pytest with test environment variables."""
    # Set test environment variables if not already set (for local testing)
    test_env = {
        "API_KEY": "test-api-key-12345678",
        "SECRET_KEY": "test-secret-key-87654321",
        'CORS_ORIGINS': '["*"]',
        "ENVIRONMENT": "testing",
        "DEBUG": "false",
        "LOG_LEVEL": "INFO",
    }

    for key, value in test_env.items():
        if key not in os.environ:
            os.environ[key] = value
