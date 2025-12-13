from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.backoffice import router as backoffice_router
from app.config import get_settings
from app.routers import operator
from app.utils.logging import setup_logging

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle management.
    Configures logging on startup and ensures clean shutdown.
    """
    try:
        setup_logging(settings.log_level)
        logging.info("Logging configured successfully")
    except Exception as exc:
        logging.basicConfig(level=logging.INFO)
        logging.error(
            "Failed to configure structured logging, falling back to basic config",
            exc_info=exc,
        )

    yield

    logging.info("Application shutdown complete")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

# ─────────────────────────────────────────────────────────────
# Middleware
# ─────────────────────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────────────────────
# Routers
# ─────────────────────────────────────────────────────────────

app.include_router(operator.router, prefix="/api", tags=["operator"])
app.include_router(backoffice_router, prefix="/admin", tags=["admin"])

# ─────────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────────


@app.get("/", response_class=JSONResponse)
async def root():
    """
    Root endpoint providing service metadata and discovery info.
    Required to satisfy quality gate tests.
    """
    return {
        "message": "Welcome to NeuroBank FastAPI Toolkit",
        "version": settings.app_version,
        "status": "operational",
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
        },
        "endpoints": {
            "health_check": "/health",
            "operator_operations": "/api",
        },
        "features": [
            "FastAPI-based banking toolkit",
            "Operator API",
            "Admin dashboard",
            "Observability & telemetry",
            "Railway-ready deployment",
        ],
    }


@app.get("/health", response_class=JSONResponse)
async def health_check():
    """
    Health check endpoint for Railway / load balancers.
    """
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
    }
