import logging
import os
import sys
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Logger de módulo (evita uso del root logger en llamadas)
logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Configuración de la aplicación optimizada para Railway"""

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    # API Configuration
    api_key: str | None = os.getenv("API_KEY")
    app_name: str = "NeuroBank FastAPI Toolkit"
    app_version: str = "1.0.0"

    # Server Configuration
    host: str = "0.0.0.0"  # nosec B104 acceptable in containerized environments  # noqa: S104
    port: int = int(os.getenv("PORT", "8000"))

    # Environment Configuration
    environment: str = os.getenv(
        "ENVIRONMENT", "development"
    )  # Default to development, not production
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"

    # CORS Configuration - usando el dominio privado de Railway
    cors_origins: list[str] = Field(default_factory=list)
    allow_origin_regex: str | None = Field(default=None)

    # AWS Configuration
    aws_region: str = os.getenv("AWS_REGION", "eu-west-1")

    # Logging Configuration
    # Sugerencias: development/testing=DEBUG, staging=INFO, production=WARNING/INFO
    log_level: str = os.getenv(
        "LOG_LEVEL", "INFO" if os.getenv("ENVIRONMENT") == "production" else "DEBUG"
    )

    # Database & JWT Configuration
    database_url: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./app.db")
    jwt_secret_key: str | None = os.getenv("JWT_SECRET_KEY")
    # Compat: soporte opcional de SECRET_KEY si existía antes
    secret_key: str | None = os.getenv("SECRET_KEY")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )
    refresh_token_expire_days: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    min_password_length: int = int(os.getenv("MIN_PASSWORD_LENGTH", "8"))

    # Railway Specific Variables (todas disponibles)
    railway_project_id: str = os.getenv("RAILWAY_PROJECT_ID", "")
    railway_environment_id: str = os.getenv("RAILWAY_ENVIRONMENT_ID", "")
    railway_service_id: str = os.getenv("RAILWAY_SERVICE_ID", "")
    railway_project_name: str = os.getenv("RAILWAY_PROJECT_NAME", "")
    railway_environment_name: str = os.getenv("RAILWAY_ENVIRONMENT_NAME", "")
    railway_service_name: str = os.getenv("RAILWAY_SERVICE_NAME", "")
    railway_private_domain: str = os.getenv("RAILWAY_PRIVATE_DOMAIN", "")

    def _get_cors_origins(self) -> list[str]:
        """Configura CORS origins usando variables de Railway"""
        # Si hay CORS_ORIGINS configurado manualmente, usarlo
        if os.getenv("CORS_ORIGINS"):
            return os.getenv("CORS_ORIGINS").split(",")

        # Si no, construir automáticamente desde Railway
        origins = ["https://*.railway.app"]

        # Añadir dominio privado de Railway si existe
        if os.getenv("RAILWAY_PRIVATE_DOMAIN"):
            origins.append(f"https://{os.getenv('RAILWAY_PRIVATE_DOMAIN')}")

        return origins

    def __init__(self, **kwargs: object) -> None:
        super().__init__(**kwargs)
        # Configurar CORS origins después de la inicialización
        self.cors_origins = self._get_cors_origins()

        # Detectar si estamos en modo test de manera más robusta
        is_testing = (
            bool(os.getenv("PYTEST_CURRENT_TEST"))
            or "pytest" in str(os.getenv("_", ""))
            or "pytest" in " ".join(sys.argv)
            or any("test" in arg for arg in sys.argv)
            or os.getenv("CI") == "true"  # GitHub Actions, GitLab CI, etc.
            or os.getenv("GITHUB_ACTIONS") == "true"  # Específico de GitHub Actions
            or self.environment
            in ["testing", "development", "dev"]  # Entornos explícitos
        )

        # En modo test o CI, asegurar que tenemos una API key
        if is_testing and not self.api_key:
            self.api_key = "test_secure_key_for_testing_only_not_production"
            logger.info(
                "🔧 Auto-configured API_KEY for testing environment (CI=%s, GITHUB_ACTIONS=%s, ENVIRONMENT=%s)",
                os.getenv("CI"),
                os.getenv("GITHUB_ACTIONS"),
                self.environment,
            )

        # En modo test o CI, asegurar secret para JWT
        if is_testing and not self.jwt_secret_key:
            self.jwt_secret_key = "test_secret_key_for_testing_only"  # noqa: S105

        # Validación de configuración crítica solo en producción real (no testing)
        if self.environment == "production" and not is_testing and not self.api_key:
            msg = "API_KEY environment variable is required in production"
            raise ValueError(msg)

        # Validación JWT estricta en producción: exigir JWT_SECRET_KEY
        if (
            self.environment == "production"
            and not is_testing
            and not self.jwt_secret_key
        ):
            msg = "JWT_SECRET_KEY environment variable is required in production"
            raise ValueError(msg)

        # Configuración CORS avanzada: origin regex basado en Railway
        private_domain = os.getenv("RAILWAY_PRIVATE_DOMAIN", "")
        if private_domain:
            # origen exacto del dominio privado
            self.cors_origins.append(f"https://{private_domain}")
        # Compat: patrón general para subdominios de Railway (usando regex, no lista)
        self.allow_origin_regex = r"^https://.*\\.railway\\.app$"


@lru_cache
def get_settings() -> Settings:
    """Obtiene la configuración de la aplicación (cached)"""
    return Settings()
