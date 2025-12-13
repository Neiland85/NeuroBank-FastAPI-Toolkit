"""
Main FastAPI application module.

This is the ONLY place where:
- FastAPI app instance is created
- Lifespan is defined
- Routers are wired
- Middleware is configured

Dependencies flow: main.py -> config.py, routers (NEVER the reverse)
"""

from contextlib import asynccontextmanager
import logging
from typing import Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.backoffice.router import router as backoffice_router
from app.config import get_settings
from app.routers import operator
from app.utils.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Configures logging on startup and ensures clean shutdown.
    """
    settings = get_settings()

    try:
        setup_logging()  # MUST be zero-arg (CodeQL)
        logging.info("Logging configured successfully")
        logging.info("Starting %s v%s", settings.app_name, settings.app_version)
        logging.info("Environment: %s", settings.environment)
    except Exception as exc:  # pragma: no cover - defensive fallback
        logging.basicConfig(level=logging.INFO)
        logging.error("Failed to configure logging, using basic config", exc_info=exc)

    yield

    logging.info("Application shutdown completed")


# -------------------------------------------------------------------
# App initialization
# -------------------------------------------------------------------

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# -------------------------------------------------------------------
# Middleware
# -------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------------
# Routers
# -------------------------------------------------------------------

app.include_router(operator.router)
app.include_router(backoffice_router)

# -------------------------------------------------------------------
# Endpoints
# -------------------------------------------------------------------


@app.get(
    "/",
    summary="API Root",
    response_description="API metadata and useful links",
)
async def root() -> Dict[str, object]:
    """Root endpoint with API information."""
    return {
        "message": f"Welcome to {settings.app_name}",
        "version": settings.app_version,
        "status": "operational",
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
        },
        "endpoints": {
            "health_check": "/health",
            "api": "/api",
            "backoffice": "/backoffice",
        },
        "features": [
            "Banking Operations API",
            "API Key Authentication",
            "Admin Backoffice Dashboard",
            "Cloud & Serverless Ready",
        ],
    }


@app.get(
    "/health",
    summary="Health check",
    response_description="Service health status",
)
async def health_check() -> JSONResponse:
    """Health check endpoint."""
    from datetime import datetime, timezone

    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": settings.app_name,
            "version": settings.app_version,
            "environment": settings.environment,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )
