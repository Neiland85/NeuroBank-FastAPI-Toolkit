import logging
import sys

from pythonjsonlogger import jsonlogger


def setup_logging():
    """Configura el sistema de logging para la aplicación"""

    # Crear formateador JSON
    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(name)s %(levelname)s %(message)s"
    )

    # Configurar handler para stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    # Configurar logger raíz
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(handler)

    # Configurar logger específico para uvicorn
    uvicorn_logger = logging.getLogger("uvicorn")
    uvicorn_logger.setLevel(logging.INFO)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Obtiene un logger configurado para el módulo especificado"""
    return logging.getLogger(name)
