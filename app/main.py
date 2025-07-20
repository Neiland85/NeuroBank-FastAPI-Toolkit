from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from .routers import operator
from .utils.logging import setup_logging

# Configuración constantes
APP_NAME = "NeuroBank FastAPI Toolkit"
APP_VERSION = "1.0.0"

# Configurar logging
setup_logging()
logger = logging.getLogger(__name__)

# Crear la aplicación FastAPI
app = FastAPI(
    title=APP_NAME,
    description="API toolkit for banking operations",
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios exactos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(operator.router, prefix="/operator", tags=["operator"])

# Health check endpoint
@app.get("/health")
async def health_check():
    """Endpoint de health check"""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": APP_NAME,
            "version": APP_VERSION
        }
    )

# Root endpoint
@app.get("/")
async def root():
    """Endpoint raíz con información básica"""
    return {
        "message": APP_NAME,
        "version": APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
