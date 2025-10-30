import logging
import sys

from pythonjsonlogger import jsonlogger

from app.config import get_settings


def setup_logging() -> None:
    """Configura el sistema de logging para la aplicación.

    Niveles sugeridos por entorno:
    - development/testing: DEBUG
    - staging: INFO
    - production: WARNING o INFO (según volumen deseado)
    """

    # Resolver nivel desde configuración dinámica
    settings = get_settings()
    try:
        level_name = (settings.log_level or "INFO").upper()
    except Exception:
        level_name = "INFO"
    level = getattr(logging, level_name, logging.INFO)

    # Crear formateador JSON
    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(name)s %(levelname)s %(message)s"
    )

    # Configurar handler para stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.setLevel(level)

    # Configurar logger raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(handler)

    # Alinear loggers de uvicorn
    logging.getLogger("uvicorn").setLevel(level)
    logging.getLogger("uvicorn.access").setLevel(level)


def get_logger(name: str) -> logging.Logger:
    """Obtiene un logger configurado para el módulo especificado"""
    return logging.getLogger(name)
