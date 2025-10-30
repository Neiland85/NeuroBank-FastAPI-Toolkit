"""
Script simple para probar el servidor FastAPI
"""

import logging
import sys
from pathlib import Path

import uvicorn

# Añadir el directorio actual al PATH
sys.path.insert(0, str(Path.cwd()))

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    logger = logging.getLogger(__name__)
    logger.info("🚀 Iniciando NeuroBank FastAPI Server...")
    logger.info("📡 URL: http://localhost:8000")
    logger.info("📊 Dashboard: http://localhost:8000/backoffice/")
    logger.info("📖 Docs: http://localhost:8000/docs")
    logger.info("%s", "=" * 50)

    try:
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",  # noqa: S104
            port=8000,
            reload=True,
            log_level="info",
        )
    except Exception:
        logger.exception("❌ Error iniciando servidor")
        sys.exit(1)
