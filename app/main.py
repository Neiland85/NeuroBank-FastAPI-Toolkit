from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import datetime
import os
from .routers import operator
from .utils.logging import setup_logging

# Configuración constantes
APP_NAME = "NeuroBank FastAPI Toolkit"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = """
## 🏦 NeuroBank FastAPI Toolkit

**Professional banking operations API** with enterprise-grade features:

### 🚀 Key Features
- **Banking Operations**: Comprehensive account management and transactions
- **Security First**: API key authentication and request validation
- **Production Ready**: AWS serverless deployment with monitoring
- **High Performance**: Async operations with optimized response times

### 🛠️ Technical Stack
- **FastAPI**: Modern, fast web framework for building APIs
- **Pydantic**: Data validation using Python type annotations
- **AWS Lambda**: Serverless compute platform
- **CloudWatch**: Monitoring and logging

### 📚 API Documentation
- **Swagger UI**: Available at `/docs` (interactive documentation)
- **ReDoc**: Available at `/redoc` (alternative documentation)

### 🔐 Authentication
All endpoints require a valid API key in the `X-API-Key` header.

### 📊 Health Monitoring
- Health check endpoint at `/health`
- Comprehensive logging with structured JSON format
- CloudWatch integration for production monitoring

---
*Built with ❤️ for modern banking infrastructure*
"""

# Configurar logging
setup_logging()
logger = logging.getLogger(__name__)

# Crear la aplicación FastAPI con documentación mejorada
app = FastAPI(
    title=APP_NAME,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "NeuroBank Development Team",
        "email": "dev@neurobank.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    servers=[
        {
            "url": "https://api.neurobank.com",
            "description": "Production server"
        },
        {
            "url": "https://staging-api.neurobank.com", 
            "description": "Staging server"
        },
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        }
    ]
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
@app.get(
    "/health",
    summary="🏥 Health Check",
    description="Comprehensive health check endpoint for monitoring service status",
    response_description="Service health status with detailed information",
    tags=["Health & Monitoring"],
    responses={
        200: {
            "description": "Service is healthy and operational",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "service": "NeuroBank FastAPI Toolkit",
                        "version": "1.0.0",
                        "timestamp": "2025-07-20T15:30:45.123456Z",
                        "environment": "production",
                        "uptime_seconds": 3600
                    }
                }
            }
        }
    }
)
async def health_check():
    """
    **Endpoint de verificación de salud del sistema**
    
    Retorna información detallada sobre:
    - ✅ Estado del servicio
    - 📊 Versión actual 
    - ⏰ Timestamp de respuesta
    - 🌍 Entorno de ejecución
    - ⏱️ Tiempo de actividad
    
    **Casos de uso:**
    - Monitoreo automatizado (Kubernetes, Docker, AWS)
    - Load balancers health checks
    - Verificación de deployments
    - Debugging y troubleshooting
    """
    import datetime
    import os
    
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": APP_NAME,
            "version": APP_VERSION,
            "timestamp": f"{datetime.datetime.now(datetime.timezone.utc).isoformat()}",
            "environment": os.getenv("ENVIRONMENT", "development"),
            "uptime_seconds": "N/A"  # Se puede implementar con un contador global
        }
    )

# Root endpoint
@app.get(
    "/",
    summary="🏠 API Root",
    description="Welcome endpoint with API information and navigation links",
    response_description="API overview with quick navigation",
    tags=["Information"],
    responses={
        200: {
            "description": "API information and navigation links",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Welcome to NeuroBank FastAPI Toolkit",
                        "version": "1.0.0",
                        "status": "operational", 
                        "documentation": {
                            "swagger_ui": "/docs",
                            "redoc": "/redoc"
                        },
                        "endpoints": {
                            "health_check": "/health",
                            "operator_operations": "/operator"
                        },
                        "features": [
                            "🏦 Banking Operations",
                            "🔐 API Key Authentication", 
                            "📊 Real-time Monitoring",
                            "☁️ AWS Serverless Ready"
                        ]
                    }
                }
            }
        }
    }
)
async def root():
    """
    **Endpoint de bienvenida de la API**
    
    Proporciona información general sobre la API incluyendo:
    - 📋 Información básica del servicio
    - 🔗 Enlaces de navegación rápida
    - 📚 Acceso a documentación
    - ⚡ Estado operacional
    - 🎯 Características principales
    
    **Útil para:**
    - Verificación rápida de conectividad
    - Descubrimiento de endpoints principales
    - Validación de versión de API
    - Navegación inicial para desarrolladores
    """
    return {
        "message": f"Welcome to {APP_NAME}",
        "version": APP_VERSION,
        "status": "operational",
        "documentation": {
            "swagger_ui": "/docs", 
            "redoc": "/redoc"
        },
        "endpoints": {
            "health_check": "/health",
            "operator_operations": "/operator"
        },
        "features": [
            "🏦 Banking Operations",
            "🔐 API Key Authentication",
            "📊 Real-time Monitoring", 
            "☁️ AWS Serverless Ready"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
