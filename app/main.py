import datetime
import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import (
    Instrumentator,  # pyright: ignore[reportMissingImports]
)

from app.auth.jwt import _get_secret
from app.backoffice import router as backoffice_router
from app.config import get_settings
from app.database import AsyncSessionLocal, init_db
from app.routers import auth as auth_router
from app.routers import operator
from app.routers import roles as roles_router
from app.routers import users as users_router
from app.services.errors import (
    EmailExistsError,
    RoleNotFoundError,
    SystemRoleDeletionError,
    UsernameExistsError,
    UserNotFoundError,
    ValidationError,
    WeakPasswordError,
)
from app.services.role_service import initialize_default_roles
from app.utils.logging import setup_logging

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


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    # Startup
    settings = get_settings()
    # Validar secreto JWT de forma temprana
    try:
        _get_secret()
    except Exception as e:
        logger.critical("JWT secret key missing or invalid during startup: %s", e)
        raise
    # Evitar create_all en producción salvo que esté explícitamente habilitado
    migrate_on_startup = os.getenv("MIGRATE_ON_STARTUP", "true").lower() == "true"
    if settings.environment != "production" and migrate_on_startup:
        await init_db()

    async with AsyncSessionLocal() as db:
        await initialize_default_roles(db)
    yield
    # Shutdown


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
        {"url": "https://api.neurobank.com", "description": "Production server"},
        {"url": "https://staging-api.neurobank.com", "description": "Staging server"},
        {"url": "http://localhost:8000", "description": "Development server"},
    ],
    lifespan=lifespan,
)

# Configurar CORS - usando configuración de Railway
settings = get_settings()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=getattr(settings, "allow_origin_regex", None),
    allow_credentials=True,
    allow_methods=["*"],  # incluye OPTIONS para preflight
    allow_headers=["*"],
)

# Exponer métricas Prometheus en /metrics (condicional)
metrics_enabled = os.getenv("METRICS_ENABLED", "true").lower() == "true"
if metrics_enabled and os.getenv("ENVIRONMENT", "development") != "production":
    Instrumentator().instrument(app).expose(app)
elif metrics_enabled and os.getenv("ENVIRONMENT") == "production":
    # Permitir habilitación explícita en producción via METRICS_ENABLED=true
    Instrumentator().instrument(app).expose(app)

# Incluir routers
app.include_router(operator.router, prefix="/api", tags=["api"])
app.include_router(auth_router.router, prefix="/api", tags=["authentication"])
app.include_router(users_router.router, prefix="/api", tags=["users"])
app.include_router(roles_router.router, prefix="/api", tags=["roles"])
app.include_router(backoffice_router.router, tags=["backoffice"])


# Manejadores globales de excepciones de dominio
@app.exception_handler(UserNotFoundError)
async def user_not_found_handler(
    _request: Request, exc: UserNotFoundError
) -> JSONResponse:  # pyright: ignore[reportGeneralTypeIssues]
    return JSONResponse(
        status_code=404, content={"detail": str(exc) or "User not found"}
    )


@app.exception_handler(UsernameExistsError)
@app.exception_handler(EmailExistsError)
async def conflict_handler(_request: Request, exc: Exception) -> JSONResponse:  # pyright: ignore[reportGeneralTypeIssues]
    return JSONResponse(
        status_code=409, content={"detail": str(exc) or "Resource conflict"}
    )


@app.exception_handler(WeakPasswordError)
@app.exception_handler(ValidationError)
async def bad_request_handler(_request: Request, exc: Exception) -> JSONResponse:  # pyright: ignore[reportGeneralTypeIssues]
    return JSONResponse(status_code=400, content={"detail": str(exc) or "Bad request"})


@app.exception_handler(RoleNotFoundError)
async def role_not_found_handler(
    _request: Request, exc: RoleNotFoundError
) -> JSONResponse:  # pyright: ignore[reportGeneralTypeIssues]
    return JSONResponse(
        status_code=404, content={"detail": str(exc) or "Role not found"}
    )


@app.exception_handler(SystemRoleDeletionError)
async def system_role_deletion_handler(
    _request: Request, exc: SystemRoleDeletionError
) -> JSONResponse:  # pyright: ignore[reportGeneralTypeIssues]
    return JSONResponse(
        status_code=400, content={"detail": str(exc) or "Business rule violation"}
    )


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
                        "uptime_seconds": 3600,
                    }
                }
            },
        }
    },
)
async def health_check() -> JSONResponse:
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
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "service": APP_NAME,
            "version": APP_VERSION,
            "timestamp": f"{datetime.datetime.now(datetime.UTC).isoformat()}",
            "environment": os.getenv("ENVIRONMENT", "production"),
            "railway": {
                "project_name": os.getenv("RAILWAY_PROJECT_NAME", "unknown"),
                "project_id": os.getenv("RAILWAY_PROJECT_ID", "unknown"),
                "service_name": os.getenv("RAILWAY_SERVICE_NAME", "unknown"),
                "environment_name": os.getenv("RAILWAY_ENVIRONMENT_NAME", "unknown"),
                "private_domain": os.getenv("RAILWAY_PRIVATE_DOMAIN", "unknown"),
            },
            "uptime_seconds": "N/A",  # Se puede implementar con un contador global
        },
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
                        "documentation": {"swagger_ui": "/docs", "redoc": "/redoc"},
                        "endpoints": {
                            "health_check": "/health",
                            "operator_operations": "/operator",
                        },
                        "features": [
                            "🏦 Banking Operations",
                            "🔐 API Key Authentication",
                            "📊 Real-time Monitoring",
                            "☁️ AWS Serverless Ready",
                        ],
                    }
                }
            },
        }
    },
)
async def root() -> dict:
    """
    **Endpoint de bienvenida de la API**

    Proporciona información general sobre la API incluyendo:
    - 📋 Información básica del servicio
    - 🔗 Enlaces de navegación rápida
    - 📚 Acceso a documentación
    - ⚡ Estado operational
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
        "documentation": {"swagger_ui": "/docs", "redoc": "/redoc"},
        "endpoints": {"health_check": "/health", "operator_operations": "/operator"},
        "features": [
            "🏦 Banking Operations",
            "🔐 API Key Authentication",
            "📊 Real-time Monitoring",
            "☁️ AWS Serverless Ready",
        ],
    }


if __name__ == "__main__":
    import uvicorn
    import uvloop

    # Use uvloop for better performance
    uvloop.install()

    port = int(os.getenv("PORT", "8000"))
    workers = int(os.getenv("WORKERS", "1"))  # Single worker for Railway

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",  # nosec B104 acceptable in dev/serverless  # noqa: S104
        port=port,
        workers=workers,
        loop="uvloop",
        access_log=True,
        timeout_keep_alive=120,
    )
