import os
import sys
from functools import lru_cache
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class BaseAppSettings(BaseSettings):
    model_config = {"extra": "ignore"}

    cors_origins: List[str] = Field(default_factory=list)

    secret_key: Optional[str] = None
    workers: int = 1
    ci: bool = False
    github_actions: bool = False

    otel_exporter_otlp_endpoint: Optional[str] = None
    otel_service_name: str = "neurobank-fastapi"
    otel_python_logging_auto_instrumentation_enabled: bool = False


class Settings(BaseAppSettings):
    """Configuración centralizada de la aplicación"""

    # API
    api_key: Optional[str] = os.getenv("API_KEY")
    app_name: str = "NeuroBank FastAPI Toolkit"
    app_version: str = "1.0.0"

    # Server
    # ❗ NO default 0.0.0.0 (Bandit B104)
    host: str = os.getenv("HOST", "127.0.0.1")
    port: int = int(os.getenv("PORT", 8000))

    # Environment
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"

    # Logging
    log_level: str = os.getenv(
        "LOG_LEVEL",
        "INFO" if environment == "production" else "DEBUG",
    )

    # Railway
    railway_private_domain: str = os.getenv("RAILWAY_PRIVATE_DOMAIN", "")

    def _get_cors_origins(self) -> List[str]:
        cors_env = os.getenv("CORS_ORIGINS")
        if cors_env:
            return [origin.strip() for origin in cors_env.split(",")]

        origins = ["https://*.railway.app"]

        if self.railway_private_domain:
            origins.append(f"https://{self.railway_private_domain}")

        return origins

    class Config:
        env_file = ".env"
        case_sensitive = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.cors_origins = self._get_cors_origins()

        is_testing = (
            bool(os.getenv("PYTEST_CURRENT_TEST"))
            or "pytest" in " ".join(sys.argv)
            or os.getenv("CI") == "true"
            or os.getenv("GITHUB_ACTIONS") == "true"
            or self.environment in {"testing", "development", "dev"}
        )

        if is_testing and not self.api_key:
            self.api_key = "test_secure_key_for_testing_only_not_production"

        if self.environment == "production" and not is_testing and not self.api_key:
            raise ValueError("API_KEY environment variable is required in production")


@lru_cache
def get_settings() -> Settings:
    return Settings()
