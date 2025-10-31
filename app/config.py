import json
import os
import sys
from functools import lru_cache
from typing import List, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración de la aplicación optimizada para Railway"""

    # API Configuration
    api_key: Optional[str] = os.getenv("API_KEY")
    app_name: str = "NeuroBank FastAPI Toolkit"
    app_version: str = "1.0.0"

    # Server Configuration
    host: str = "0.0.0.0"
    port: int = int(os.getenv("PORT", 8000))
    workers: int = int(os.getenv("WORKERS", 1))

    # Security / Secrets
    secret_key: Optional[str] = os.getenv("SECRET_KEY")

    # Environment Configuration
    environment: str = os.getenv(
        "ENVIRONMENT", "development"
    )  # Default to development, not production
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"

    # CORS Configuration: definir como string para evitar parseo JSON automático
    cors_origins: Optional[str] = os.getenv("CORS_ORIGINS")

    # AWS Configuration
    aws_region: str = os.getenv("AWS_REGION", "eu-west-1")

    # Logging Configuration
    log_level: str = os.getenv(
        "LOG_LEVEL", "INFO" if os.getenv("ENVIRONMENT") == "production" else "DEBUG"
    )

    # Railway Specific Variables (todas disponibles)
    railway_project_id: str = os.getenv("RAILWAY_PROJECT_ID", "")
    railway_environment_id: str = os.getenv("RAILWAY_ENVIRONMENT_ID", "")
    railway_service_id: str = os.getenv("RAILWAY_SERVICE_ID", "")
    railway_project_name: str = os.getenv("RAILWAY_PROJECT_NAME", "")
    railway_environment_name: str = os.getenv("RAILWAY_ENVIRONMENT_NAME", "")
    railway_service_name: str = os.getenv("RAILWAY_SERVICE_NAME", "")
    railway_private_domain: str = os.getenv("RAILWAY_PRIVATE_DOMAIN", "")

    def _get_cors_origins(self) -> List[str]:
        """Configura CORS origins usando variables de Railway"""
        # Si hay CORS_ORIGINS configurado manualmente, usarlo con parseo robusto
        raw = self.cors_origins
        if raw is not None:
            raw_str = raw.strip()
            if raw_str == "":
                return []
            try:
                parsed = json.loads(raw_str)
                if isinstance(parsed, list):
                    return [str(x).strip() for x in parsed if str(x).strip()]
            except Exception:
                return [part.strip() for part in raw_str.split(",") if part.strip()]

        # Si no, construir automáticamente desde Railway
        origins = ["https://*.railway.app"]

        # Añadir dominio privado de Railway si existe
        if os.getenv("RAILWAY_PRIVATE_DOMAIN"):
            origins.append(f"https://{os.getenv('RAILWAY_PRIVATE_DOMAIN')}")

        return origins

    class Config:
        env_file = ".env"
        case_sensitive = False

    def __init__(self, **kwargs):
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
            print(
                f"🔧 Auto-configured API_KEY for testing environment (CI={os.getenv('CI')}, GITHUB_ACTIONS={os.getenv('GITHUB_ACTIONS')}, ENVIRONMENT={self.environment})"
            )

        # Validación de configuración crítica solo en producción real (no testing)
        if self.environment == "production" and not is_testing and not self.api_key:
            raise ValueError("API_KEY environment variable is required in production")


@lru_cache()
def get_settings() -> Settings:
    """Obtiene la configuración de la aplicación (cached)"""
    return Settings()
