"""
Application configuration and settings.

This module provides a centralized configuration management system using Pydantic.
It MUST NOT import FastAPI, routers, or app.main to avoid circular dependencies.
"""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "NeuroBank FastAPI Toolkit"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = False

    # Security
    api_key: str = ""
    secret_key: str = ""

    # CORS
    cors_origins: List[str] = ["*"]

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra environment variables

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Uses lru_cache to ensure settings are loaded once and reused.
    This avoids repeated environment variable reads.
    """
    return Settings()
