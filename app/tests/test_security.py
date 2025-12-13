"""Tests for security module."""

import os
from unittest.mock import patch

import pytest

from app.security import (
    configure_production_logging,
    generate_secure_keys,
    security_health_check,
    validate_production_config,
)


class TestConfigureProductionLogging:
    """Tests for configure_production_logging function."""

    def test_configure_logging_default_level(self):
        """Test logging configuration with default INFO level."""
        with patch.dict(os.environ, {}, clear=False):
            configure_production_logging()

    def test_configure_logging_debug_level(self):
        """Test logging configuration with DEBUG level."""
        with patch.dict(os.environ, {"LOG_LEVEL": "DEBUG"}, clear=False):
            configure_production_logging()

    def test_configure_logging_production_environment(self):
        """Test logging configuration in production environment."""
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}, clear=False):
            configure_production_logging()


class TestGenerateSecureKeys:
    """Tests for generate_secure_keys function."""

    def test_generate_keys_returns_dict(self):
        """Test that generate_secure_keys returns a dictionary."""
        keys = generate_secure_keys()
        assert isinstance(keys, dict)
        assert "api_key" in keys
        assert "secret_key" in keys

    def test_generate_keys_are_unique(self):
        """Test that each call generates unique keys."""
        keys1 = generate_secure_keys()
        keys2 = generate_secure_keys()
        assert keys1["api_key"] != keys2["api_key"]
        assert keys1["secret_key"] != keys2["secret_key"]

    def test_generate_keys_sufficient_length(self):
        """Test that generated keys have sufficient length."""
        keys = generate_secure_keys()
        assert len(keys["api_key"]) >= 32
        assert len(keys["secret_key"]) >= 32


class TestValidateProductionConfig:
    """Tests for validate_production_config function."""

    def test_valid_config(self):
        """Test validation with valid configuration."""
        env = {
            "API_KEY": "test-api-key-12345678901234567890",
            "SECRET_KEY": "test-secret-key-12345678901234567890",
            "CORS_ORIGINS": "https://example.com",
            "ENVIRONMENT": "production",
        }
        with patch.dict(os.environ, env, clear=False):
            result = validate_production_config()
            assert result["valid"] is True
            assert len(result["errors"]) == 0

    def test_missing_api_key(self):
        """Test validation with missing API_KEY."""
        env = {"SECRET_KEY": "test-secret", "API_KEY": ""}
        with patch.dict(os.environ, env, clear=False):
            os.environ.pop("API_KEY", None)
            result = validate_production_config()
            assert any("API_KEY" in e for e in result["errors"])

    def test_short_api_key_warning(self):
        """Test warning for short API key."""
        env = {
            "API_KEY": "short",
            "SECRET_KEY": "test-secret",
            "CORS_ORIGINS": "https://example.com",
        }
        with patch.dict(os.environ, env, clear=False):
            result = validate_production_config()
            assert any("16 characters" in w for w in result["warnings"])

    def test_wildcard_cors_error(self):
        """Test error for wildcard CORS origins."""
        env = {
            "API_KEY": "test-api-key-12345678901234567890",
            "SECRET_KEY": "test-secret",
            "CORS_ORIGINS": "*",
        }
        with patch.dict(os.environ, env, clear=False):
            result = validate_production_config()
            assert any("wildcard" in e for e in result["errors"])

    def test_non_production_environment_warning(self):
        """Test warning for non-production environment."""
        env = {
            "API_KEY": "test-api-key-12345678901234567890",
            "SECRET_KEY": "test-secret",
            "CORS_ORIGINS": "https://example.com",
            "ENVIRONMENT": "development",
        }
        with patch.dict(os.environ, env, clear=False):
            result = validate_production_config()
            assert any("production-ready" in w for w in result["warnings"])


class TestSecurityHealthCheck:
    """Tests for security_health_check function."""

    def test_healthy_status(self):
        """Test health check with valid configuration."""
        env = {
            "API_KEY": "test-api-key-12345678901234567890",
            "SECRET_KEY": "test-secret-key-12345678901234567890",
            "CORS_ORIGINS": "https://example.com",
            "ENVIRONMENT": "production",
        }
        with patch.dict(os.environ, env, clear=False):
            result = security_health_check()
            assert result["security_status"] == "healthy"

    def test_unhealthy_status(self):
        """Test health check with invalid configuration."""
        env = {"CORS_ORIGINS": "*", "API_KEY": "", "SECRET_KEY": ""}
        with patch.dict(os.environ, env, clear=False):
            os.environ.pop("API_KEY", None)
            os.environ.pop("SECRET_KEY", None)
            result = security_health_check()
            assert result["security_status"] == "unhealthy"
