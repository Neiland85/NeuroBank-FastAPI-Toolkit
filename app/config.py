import os
import sys
from functools import lru_cache
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class BaseAppSettings(BaseSettings):
    model_config = {"extra": "ignore"}

    cors_origins: list[str] = Field(default_factory=list)

    # Opcionales
    secret_key: str | None = None
    workers: int | None = 1
    ci: bool | None = False
    github_actions: bool | None = False

    # OpenTelemetry
    otel_exporter_otlp_endpoint: str | None = None
    otel_service_name: str | None = "neurobank-fastapi"
    otel_python_logging_auto_instrumentation_enabled: bool | None = False


class Settings(BaseAppSettings):
    """Configuración de la aplicación optimizada para Railway y CI"""

    # API
    api_key: Optional[str] = os.getenv("API_KEY")
    app_name: str = "NeuroBank FastAPI Toolkit"
    app_version: str = "1.0.0"

    # Server (⚠️ NO hardcodear 0.0.0.0)
    host: str = os.getenv("HOST", "127.0.0.1")
    port: int = int(os.getenv("PORT", 8000))

    # Environment
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"

    # CORS
    cors_origins: List[str] = []

    # AWS
    aws_region: str = os.getenv("AWS_REGION", "eu-west-1")

    # Logging
    log_level: str = os.getenv(
        "LOG_LEVEL",
        "INFO" if os.getenv("ENVIRONMENT") == "production" else "DEBUG",
    )

    # Railway
    railway_project_id: str = os.getenv("RAILWAY_PROJECT_ID", "")
    railway_environment_id: str = os.getenv("RAILWAY_ENVIRONMENT_ID", "")
    railway_service_id: str = os.getenv("RAILWAY_SERVICE_ID", "")
    railway_project_name: str = os.getenv("RAILWAY_PROJECT_NAME", "")
    railway_environment_name: str = os.getenv("RAILWAY_ENVIRONMENT_NAME", "")
    railway_service_name: str = os.getenv("RAILWAY_SERVICE_NAME", "")
    railway_private_domain: str = os.getenv("RAILWAY_PRIVATE_DOMAIN", "")

    def _get_cors_origins(self) -> List[str]:
        if os.getenv("CORS_ORIGINS"):
            return os.getenv("CORS_ORIGINS").split(",")

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


@lru_cache()
def get_settings() -> Settings:
    return Settings()
