"""
Main FastAPI application module.

This is the ONLY place where:
- FastAPI app instance is created
- Lifespan is defined
- Routers are wired
- Middleware is configured

Dependencies flow: main.py -> config.py, routers (NEVER the reverse)
"""

import logging
from contextlib import asynccontextmanager
from typing import Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.backoffice.router import router as backoffice_router
from app.routers import operator
from app.utils.logging import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Configures logging on startup and ensures clean shutdown.
    Settings are imported lazily inside the function to avoid circular imports.
    """
    # Lazy import to avoid circular dependency
    from app.config import get_settings

    settings = get_settings()

    # Startup
    try:
        setup_logging()  # NO arguments - CodeQL requirement
        logging.info("Logging configured successfully")
        logging.info(f"Starting {settings.app_name} v{settings.app_version}")
        logging.info(f"Environment: {settings.environment}")
    except Exception as exc:
        logging.basicConfig(level=logging.INFO)
        logging.error("Failed to configure logging, using basic config", exc_info=exc)

    yield

    # Shutdown
    logging.info("Application shutdown completed")


# Lazy settings access
from app.config import get_settings

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(operator.router, prefix="/api", tags=["API"])
app.include_router(backoffice_router)


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
            "operator_operations": "/api",
            "backoffice": "/backoffice",
        },
        "features": [
            "🏦 Banking Operations",
            "🔐 API Key Authentication",
            "📊 Admin Backoffice Dashboard",
            "☁️ Cloud & Serverless Ready",
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
