import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.backoffice.router import router as backoffice_router
from app.config import get_settings
from app.routers import operator
from app.utils.logging import setup_logging

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Configures logging safely on startup and ensures clean shutdown.
    """
    try:
        setup_logging()  # ⚠️ SIN ARGUMENTOS (CodeQL FIX)
        logging.info("Logging configured successfully")
    except Exception as exc:
        logging.basicConfig(level=logging.INFO)
        logging.error("Failed to configure logging, using basic config", exc_info=exc)

    yield

    logging.info("Application shutdown completed")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(operator.router, prefix="/api", tags=["API"])
app.include_router(backoffice_router)  # el prefijo vive en el router


@app.get(
    "/",
    summary="🏠 API Root",
    response_class=JSONResponse,
)
async def root():
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
            "🏦 Banking Operations",
            "🔐 API Key Authentication",
            "📊 Admin Backoffice Dashboard",
            "☁️ Cloud & Serverless Ready",
        ],
    }
