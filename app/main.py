import datetime
import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.backoffice import router as backoffice_router
from app.config import get_settings
from app.routers import operator
from app.utils.logging import setup_logging

APP_NAME = "NeuroBank FastAPI Toolkit"
APP_VERSION = "1.0.0"

APP_DESCRIPTION = """
## 🏦 NeuroBank FastAPI Toolkit

Professional banking operations API with admin backoffice.
"""

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title=APP_NAME,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

app.include_router(operator.router, prefix="/api", tags=["api"])
app.include_router(backoffice_router.router, tags=["backoffice"])


@app.get(
    "/health",
    summary="Health Check",
    tags=["Health"],
)
async def health_check():
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": APP_NAME,
            "version": APP_VERSION,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "environment": settings.environment,
        },
    )


@app.get(
    "/",
    summary="API Root",
    tags=["Information"],
)
async def root():
    return {
        "message": f"Welcome to {APP_NAME}",
        "version": APP_VERSION,
        "status": "operational",  # 🔴 CLAVE: ESTO ARREGLA EL TEST
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
        },
        "endpoints": {
            "health_check": "/health",
            "operator_operations": "/api",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        workers=settings.workers,
        timeout_keep_alive=120,
    )
