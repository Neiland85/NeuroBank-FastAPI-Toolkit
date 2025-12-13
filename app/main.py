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
    try:
        setup_logging()
        logging.info("Logging configured successfully")
    except Exception as exc:
        logging.basicConfig(level=logging.INFO)
        logging.error(f"Failed to configure logging: {exc}")

    yield

    logging.info("Application shutdown")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=JSONResponse)
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
            "FastAPI",
            "Pydantic v2",
            "AsyncIO",
            "Structured logging",
        ],
    }


app.include_router(operator.router, prefix="/api")
app.include_router(backoffice_router, prefix="/backoffice")
