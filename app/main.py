from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import logging
import datetime
import os
from .routers import operator
from .backoffice import router as backoffice_router
from .utils.logging import setup_logging

# Configuración constantes
APP_NAME = "NeuroBank FastAPI Toolkit"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = """
## 🏦 NeuroBank FastAPI Toolkit

**Professional banking operations API** with enterprise-grade features and **admin backoffice dashboard**:

### 🚀 Key Features
- **Banking Operations**: Comprehensive account management and transactions
- **Admin Dashboard**: Visual backoffice panel at `/backoffice/` with real-time metrics
- **Security First**: API key authentication and request validation
- **Production Ready**: AWS serverless deployment with monitoring
- **High Performance**: Async operations with optimized response times

### 🎨 Backoffice Dashboard
- **Real-time Metrics**: Live transaction monitoring and system health
- **Interactive Charts**: Chart.js visualizations for business intelligence
- **Transaction Management**: Advanced filtering and administration tools
- **Responsive Design**: Bootstrap 5 with professional banking UI
- **Protected Admin Panels**: Secure administrative access

### 🛠️ Technical Stack
- **FastAPI**: Modern, fast web framework for building APIs
- **Jinja2**: Template engine for dynamic HTML generation
- **Bootstrap 5**: Professional UI framework with responsive design
- **Chart.js**: Interactive data visualizations
- **Pydantic**: Data validation using Python type annotations
- **AWS Lambda**: Serverless compute platform
- **CloudWatch**: Monitoring and logging

### 📚 API Documentation
- **Swagger UI**: Available at `/docs` (interactive documentation)
- **ReDoc**: Available at `/redoc` (alternative documentation)
- **Admin Dashboard**: Available at `/backoffice/` (visual interface)

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

# Configurar CORS - usando configuración de Railway
from .config import get_settings
settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(operator.router, prefix="/operator", tags=["operator"])
app.include_router(backoffice_router.router, tags=["backoffice"])

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
            "environment": os.getenv("ENVIRONMENT", "production"),
            "railway": {
                "project_name": os.getenv("RAILWAY_PROJECT_NAME", "unknown"),
                "project_id": os.getenv("RAILWAY_PROJECT_ID", "unknown"),
                "service_name": os.getenv("RAILWAY_SERVICE_NAME", "unknown"),
                "environment_name": os.getenv("RAILWAY_ENVIRONMENT_NAME", "unknown"),
                "private_domain": os.getenv("RAILWAY_PRIVATE_DOMAIN", "unknown")
            },
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
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
