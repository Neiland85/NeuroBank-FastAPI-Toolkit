"""
Application configuration and settings.

Centralized configuration management using Pydantic Settings.
This module MUST NOT import FastAPI, routers, or app.main
to avoid circular dependencies.
"""

from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # ------------------------------------------------------------------
    # Application
    # ------------------------------------------------------------------
    app_name: str = "NeuroBank FastAPI Toolkit"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = False

    # ------------------------------------------------------------------
    # Security
    # ------------------------------------------------------------------
    api_key: str = Field(default="", repr=False)
    secret_key: str = Field(default="", repr=False)

    # ------------------------------------------------------------------
    # CORS
    # ------------------------------------------------------------------
    cors_origins: List[str] = Field(default_factory=lambda: ["*"])

    # ------------------------------------------------------------------
    # Logging
    # ------------------------------------------------------------------
    log_level: str = "INFO"

    # ------------------------------------------------------------------
    # Pydantic Settings config (v2 style)
    # ------------------------------------------------------------------
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def is_production(self) -> bool:
        """Return True if running in production environment."""
        return self.environment.lower() == "production"

    @property
    def security_enabled(self) -> bool:
        """Check whether security credentials are configured."""
        return bool(self.api_key and self.secret_key)


@lru_cache
def get_settings() -> Settings:
    """
    Return cached Settings instance.

    Ensures environment variables are read once
    and prevents configuration drift.
    """
    return Settings()
