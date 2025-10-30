# Security Configuration for Production
import logging
import os
import secrets
from typing import Any


# Configure logging for production
def configure_production_logging() -> None:
    """Configure secure logging for production"""
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    # Configure structured logging
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Disable debug logs in production
    if os.getenv("ENVIRONMENT") == "production":
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def generate_secure_keys() -> dict[str, str]:
    """Generate secure keys for production use"""
    return {
        "api_key": secrets.token_urlsafe(32),
        "secret_key": secrets.token_urlsafe(32),
    }


def validate_production_config() -> dict[str, Any]:
    """Validate critical production configuration"""
    errors: list[str] = []
    warnings = []

    # Check critical environment variables
    required_vars = ["API_KEY", "SECRET_KEY"]
    errors = errors + [
        f"Missing required environment variable: {var}"
        for var in required_vars
        if not os.getenv(var)
    ]

    # Check API key strength
    api_key = os.getenv("API_KEY", "")
    min_api_key_len = 16
    if len(api_key) < min_api_key_len:
        warnings.append("API_KEY should be at least 16 characters long")

    # Check CORS configuration
    cors_origins = os.getenv("CORS_ORIGINS", "")
    if "*" in cors_origins:
        errors.append(
            "CORS_ORIGINS contains wildcard (*) - security risk in production"
        )

    # Check environment
    environment = os.getenv("ENVIRONMENT", "development")
    if environment not in ["production", "staging"]:
        warnings.append(f"Environment '{environment}' may not be production-ready")

    return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}


# Health check with security validation
def security_health_check() -> dict[str, Any]:
    """Perform security-focused health check"""
    config_check = validate_production_config()

    return {
        "security_status": "healthy" if config_check["valid"] else "unhealthy",
        "environment": os.getenv("ENVIRONMENT", "unknown"),
        "cors_configured": bool(os.getenv("CORS_ORIGINS")),
        "api_key_configured": bool(os.getenv("API_KEY")),
        "secret_key_configured": bool(os.getenv("SECRET_KEY")),
        "issues": config_check["errors"] + config_check["warnings"],
    }
