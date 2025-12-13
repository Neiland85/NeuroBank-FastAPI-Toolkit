from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.backoffice import router as backoffice_router
from app.config import get_settings
from app.routers import operator
from app.utils.logging import setup_logging

settings = get_settings()

setup_logging(settings.log_level)

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
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
app.include_router(operator.router, prefix="/api", tags=["operator"])
app.include_router(backoffice_router, prefix="/backoffice", tags=["backoffice"])


@app.get("/", response_class=JSONResponse)
async def root():
    """Root endpoint with service metadata"""
    return {
        "message": "Welcome to NeuroBank FastAPI Toolkit",
        "status": "operational",
        "version": settings.app_version,
        "documentation": {
            "swagger_ui": "/docs",
            "redoc": "/redoc",
        },
        "endpoints": {
            "health_check": "/health",
            "operator_operations": "/api",
        },
        "features": [
            "fastapi",
            "hexagonal-architecture",
            "async-ready",
            "security-first",
            "ci-cd-enabled",
            "observability-ready",
        ],
    }


@app.get("/health", response_class=JSONResponse)
async def health_check():
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": settings.app_version,
    }
