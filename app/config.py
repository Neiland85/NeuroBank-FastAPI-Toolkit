import os
from functools import lru_cache
from pydantic import BaseSettings

class Settings(BaseSettings):
    """Configuración de la aplicación"""
    
    # API Configuration
    api_key: str = os.getenv("API_KEY", "default-test-key")
    app_name: str = "NeuroBank FastAPI Toolkit"
    app_version: str = "1.0.0"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # AWS Configuration
    aws_region: str = os.getenv("AWS_REGION", "eu-west-1")
    
    # Logging Configuration
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    """Obtiene la configuración de la aplicación (cached)"""
    return Settings()
