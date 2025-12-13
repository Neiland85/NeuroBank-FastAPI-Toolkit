import logging
from contextlib import asynccontextmanager
from typing import Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.backoffice.router import router as backoffice_router
from app.config import get_settings
from app.routers import operator
from app.utils.logging import setup_logging

# -------------------------------------------------------------------
# Settings
# -------------------------------------------------------------------

settings = get_settings()

APP_NAME = settings.app_name
APP_VERSION = settings.app_version

# -------------------------------------------------------------------
# Lifespan
# -------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        setup_logging(settings.log_level)
        logging.info("Logging configured")
    except Exception as exc:  # pragma: no cover
        logging.basicConfig(level=logging.INFO)
        logging.error("Logging fallback activated: %s", exc)

    yield

    logging.info("Application shutdown complete")


# -------------------------------------------------------------------
# App
# -------------------------------------------------------------------

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
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

app.include_router(operator.router, prefix="/api", tags=["api"])
app.include_router(backoffice_router, prefix="/backoffice")

# -------------------------------------------------------------------
# Endpoints
# -------------------------------------------------------------------


@app.get("/")
async def root() -> Dict[str, object]:
    return {
        "message": f"Welcome to {APP_NAME}",
        "version": APP_VERSION,
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
            "📊 Admin Dashboard",
            "☁️ Railway Ready",
        ],
    }


@app.get("/health")
async def health_check() -> JSONResponse:
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": APP_NAME,
            "version": APP_VERSION,
            "environment": settings.environment,
        },
    )
