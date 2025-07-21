import os
import sys
from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    """Configuración de la aplicación optimizada para Railway"""
    
    # API Configuration
    api_key: Optional[str] = os.getenv("API_KEY")
    app_name: str = "NeuroBank FastAPI Toolkit"
    app_version: str = "1.0.0"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = int(os.getenv("PORT", 8000))
    
    # Environment Configuration
       develop
    environment: str = os.getenv("ENVIRONMENT", "production")

    environment: str = os.getenv("ENVIRONMENT", "development")  # Default to development, not production
      main
    debug: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # CORS Configuration - usando el dominio privado de Railway
    cors_origins: List[str] = []
    
    # AWS Configuration
    aws_region: str = os.getenv("AWS_REGION", "eu-west-1")
    
    # Logging Configuration
    log_level: str = os.getenv("LOG_LEVEL", "INFO" if os.getenv("ENVIRONMENT") == "production" else "DEBUG")
    
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
        # Si hay CORS_ORIGINS configurado manualmente, usarlo
        if os.getenv("CORS_ORIGINS"):
            return os.getenv("CORS_ORIGINS").split(",")
        
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
        
        develop
        # Detectar si estamos en modo test
        is_testing = bool(os.getenv("PYTEST_CURRENT_TEST")) or "pytest" in os.getenv("_", "")
        
        # Validación de configuración crítica solo en producción (no en tests)
        if self.environment == "production" and not is_testing and not self.api_key:
            raise ValueError("API_KEY environment variable is required in production")
        
        # Si estamos en tests y no hay API_KEY, usar una de prueba
        if is_testing and not self.api_key:
            self.api_key = "test_secure_key_for_testing_only_not_production"

        # Detectar si estamos en modo test de manera más robusta
        is_testing = (
            bool(os.getenv("PYTEST_CURRENT_TEST")) or 
            "pytest" in str(os.getenv("_", "")) or
            "pytest" in " ".join(sys.argv) or
            any("test" in arg for arg in sys.argv) or
            os.getenv("CI") == "true" or  # GitHub Actions, GitLab CI, etc.
            os.getenv("GITHUB_ACTIONS") == "true" or  # Específico de GitHub Actions
            self.environment in ["testing", "development", "dev"]  # Entornos explícitos
        )
        
        # En modo test o CI, asegurar que tenemos una API key
        if is_testing and not self.api_key:
            self.api_key = "test_secure_key_for_testing_only_not_production"
            print(f"🔧 Auto-configured API_KEY for testing environment (CI={os.getenv('CI')}, GITHUB_ACTIONS={os.getenv('GITHUB_ACTIONS')}, ENVIRONMENT={self.environment})")
        
        # Validación de configuración crítica solo en producción real (no testing)
        if (self.environment == "production" and 
            not is_testing and 
            not self.api_key):
            raise ValueError("API_KEY environment variable is required in production")
         main

@lru_cache()
def get_settings() -> Settings:
    """Obtiene la configuración de la aplicación (cached)"""
    return Settings()
