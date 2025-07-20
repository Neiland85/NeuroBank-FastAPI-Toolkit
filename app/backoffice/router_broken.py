"""
🏦 NeuroBank Backoffice Dashboard Router
Enterprise-grade admin panel para impresionar reclutadores bancarios
"""

from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timedelta
from typing import Dict, List, Any
from pydantic import BaseModel, Field
import random
from decimal import Decimal
import uuid
from enum import Enum
            "Bootstrap 5 for UI",
            "Real-time data updates"
        ]
    }

# ================================
# 🔍 API ENDPOINTS FOR FILTERS & SEARCH
# ================================

@router.get("/api/transactions/search")
async def search_transactions(
    query: str = "",
    status: str = "",
    transaction_type: str = "",
    date_from: str = "",
    date_to: str = "",
    page: int = 1,
    page_size: int = 20
):
    """
    🔍 **API de Búsqueda y Filtrado de Transacciones**
    
    Endpoint para filtrar transacciones con múltiples criterios.
    """
    # Generar transacciones mock para la demo
    all_transactions = generate_mock_transactions(200)
    
    # Filtrar por query general
    if query:
        filtered = [
            t for t in all_transactions 
            if query.lower() in t.get("reference", "").lower() or
               query.lower() in t.get("description", "").lower() or
               query.lower() in str(t.get("user_id", "")).lower()
        ]
    else:
        filtered = all_transactions
    
    # Filtrar por estado
    if status:
        filtered = [t for t in filtered if t.get("status") == status]
    
    # Filtrar por tipo
    if transaction_type:
        filtered = [t for t in filtered if t.get("type") == transaction_type]
    
    # Filtrar por fechas
    if date_from or date_to:
        from datetime import datetime as dt
        try:
            if date_from:
                date_from_obj = dt.fromisoformat(date_from.replace('Z', '+00:00'))
                filtered = [t for t in filtered 
                           if dt.fromisoformat(t["created_at"].replace('Z', '+00:00')) >= date_from_obj]
            if date_to:
                date_to_obj = dt.fromisoformat(date_to.replace('Z', '+00:00'))
                filtered = [t for t in filtered 
                           if dt.fromisoformat(t["created_at"].replace('Z', '+00:00')) <= date_to_obj]
        except:
            pass  # Si hay error en las fechas, ignoramos el filtro
    
    # Paginación
    total = len(filtered)
    start = (page - 1) * page_size
    end = start + page_size
    paginated = filtered[start:end]
    
    return {
        "transactions": paginated,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }

@router.get("/api/transactions/export")
async def export_transactions(
    format: str = "csv",
    status: str = "",
    transaction_type: str = "",
    date_from: str = "",
    date_to: str = ""
):
    """
    📊 **Exportar Transacciones**
    
    Exporta transacciones filtradas en diferentes formatos.
    """
    # Para la demo, retornamos una URL de descarga simulada
    export_data = {
        "download_url": f"/backoffice/api/download/transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format}",
        "total_records": random.randint(100, 500),
        "format": format,
        "generated_at": datetime.now().isoformat()
    }
    
    return export_datag import Dict, List, Any
from pydantic import BaseModel, Field
import random
from decimal import Decimal
import uuid
from enum import Enum

# Router configuration
router = APIRouter(prefix="/backoffice", tags=["Backoffice Dashboard"])
templates = Jinja2Templates(directory="app/backoffice/templates")

# ================================
# 📊 MODELS FOR DASHBOARD DATA
# ================================

class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TransactionType(str, Enum):
    TRANSFER = "transfer"
    DEPOSIT = "deposit"
    WITHDRAWAL = "withdrawal"
    PAYMENT = "payment"

class DashboardMetrics(BaseModel):
    """Métricas principales del dashboard"""
    total_transactions: int = Field(..., description="Total de transacciones hoy")
    total_volume: Decimal = Field(..., description="Volumen total en USD")
    active_accounts: int = Field(..., description="Cuentas activas")
    success_rate: float = Field(..., description="Tasa de éxito de transacciones")
    avg_response_time: float = Field(..., description="Tiempo de respuesta promedio (ms)")
    api_calls_today: int = Field(..., description="Llamadas API hoy")
    
class Transaction(BaseModel):
    """Modelo de transacción para el dashboard"""
    id: str = Field(..., description="ID único de transacción")
    type: TransactionType = Field(..., description="Tipo de transacción")
    status: TransactionStatus = Field(..., description="Estado de la transacción")
    amount: Decimal = Field(..., description="Monto de la transacción")
    currency: str = Field(default="USD", description="Moneda")
    from_account: str = Field(..., description="Cuenta origen")
    to_account: str = Field(..., description="Cuenta destino")
    timestamp: datetime = Field(..., description="Timestamp de la transacción")
    description: str = Field(..., description="Descripción")

class SystemHealth(BaseModel):
    """Estado del sistema"""
    status: str = Field(..., description="Estado general del sistema")
    uptime: str = Field(..., description="Tiempo de actividad")
    cpu_usage: float = Field(..., description="Uso de CPU (%)")
    memory_usage: float = Field(..., description="Uso de memoria (%)")
    database_status: str = Field(..., description="Estado de la base de datos")
    api_gateway_status: str = Field(..., description="Estado del API Gateway")
    lambda_cold_starts: int = Field(..., description="Cold starts de Lambda")

# ================================
# 🎲 MOCK DATA GENERATORS
# ================================

def generate_mock_transactions(count: int = 50) -> List[Transaction]:
    """Genera transacciones mock para el dashboard"""
    transactions = []
    
    account_prefixes = ["ACC", "BNK", "CRP", "PRS"]
    descriptions = [
        "Online purchase", "ATM withdrawal", "Salary deposit", 
        "Bill payment", "International transfer", "Mobile payment",
        "Investment purchase", "Loan payment", "Insurance premium"
    ]
    
    for _ in range(count):
        transaction = Transaction(
            id=f"TXN-{uuid.uuid4().hex[:8].upper()}",
            type=random.choice(list(TransactionType)),
            status=random.choice(list(TransactionStatus)),
            amount=Decimal(str(round(random.uniform(10.0, 50000.0), 2))),
            currency="USD",
            from_account=f"{random.choice(account_prefixes)}-{random.randint(1000000, 9999999)}",
            to_account=f"{random.choice(account_prefixes)}-{random.randint(1000000, 9999999)}",
            timestamp=datetime.now() - timedelta(
                hours=random.randint(0, 72),
                minutes=random.randint(0, 59)
            ),
            description=random.choice(descriptions)
        )
        transactions.append(transaction)
    
    # Ordenar por timestamp descendente
    transactions.sort(key=lambda x: x.timestamp, reverse=True)
    return transactions

def generate_dashboard_metrics() -> DashboardMetrics:
    """Genera métricas mock para el dashboard"""
    return DashboardMetrics(
        total_transactions=random.randint(1200, 2500),
        total_volume=Decimal(str(round(random.uniform(500000, 2000000), 2))),
        active_accounts=random.randint(450, 850),
        success_rate=round(random.uniform(97.5, 99.9), 2),
        avg_response_time=round(random.uniform(120, 380), 1),
        api_calls_today=random.randint(5000, 15000)
    )

def generate_system_health() -> SystemHealth:
    """Genera datos de salud del sistema"""
    return SystemHealth(
        status="healthy",
        uptime="15 days, 7 hours",
        cpu_usage=round(random.uniform(25, 75), 1),
        memory_usage=round(random.uniform(40, 80), 1),
        database_status="operational",
        api_gateway_status="operational", 
        lambda_cold_starts=random.randint(5, 25)
    )

# ================================
# 🎨 DASHBOARD ENDPOINTS
# ================================

@router.get("/", response_class=HTMLResponse, summary="Admin Dashboard Principal")
async def dashboard_home(request: Request):
    """
    🏦 **NeuroBank Admin Dashboard**
    
    Dashboard principal del backoffice con métricas en tiempo real,
    transacciones recientes y estado del sistema.
    
    **Características:**
    - Métricas financieras en tiempo real
    - Visualización de transacciones recientes  
    - Monitoreo de salud del sistema
    - Gráficos interactivos con Chart.js
    - Diseño responsive y profesional
    """
    return templates.TemplateResponse("basic_dashboard.html", {
        "request": request,
        "title": "NeuroBank Admin Dashboard"
    })

@router.get("/api/metrics", response_model=DashboardMetrics, summary="Métricas del Dashboard")
async def get_dashboard_metrics():
    """
    📊 **API de Métricas del Dashboard**
    
    Devuelve métricas en tiempo real para el dashboard administrativo.
    
    **Métricas incluidas:**
    - Total de transacciones del día
    - Volumen total procesado
    - Cuentas activas
    - Tasa de éxito de transacciones
    - Tiempo de respuesta promedio
    - Llamadas API del día
    """
    return generate_dashboard_metrics()

@router.get("/api/transactions", response_model=List[Transaction], summary="Transacciones Recientes")
async def get_recent_transactions(limit: int = 20):
    """
    💳 **API de Transacciones Recientes**
    
    Devuelve las transacciones más recientes para mostrar en el dashboard.
    
    **Parámetros:**
    - `limit`: Número máximo de transacciones a devolver (default: 20)
    
    **Tipos de transacción soportados:**
    - Transferencias
    - Depósitos  
    - Retiros
    - Pagos
    """
    transactions = generate_mock_transactions(50)
    return transactions[:limit]

@router.get("/api/system-health", response_model=SystemHealth, summary="Estado del Sistema")
async def get_system_health():
    """
    🏥 **API de Salud del Sistema**
    
    Monitoreo en tiempo real del estado de todos los componentes del sistema.
    
    **Componentes monitoreados:**
    - Estado general del sistema
    - Tiempo de actividad (uptime)
    - Uso de recursos (CPU, memoria)
    - Estado de base de datos
    - Estado del API Gateway
    - Cold starts de Lambda functions
    """
    return generate_system_health()

@router.get("/api/charts/transactions-by-hour", summary="Datos para Gráfico de Transacciones por Hora")
async def get_transactions_by_hour() -> Dict[str, Any]:
    """
    📈 **API para Gráfico de Transacciones por Hora**
    
    Devuelve datos para generar gráfico de barras con transacciones por hora.
    Usado para visualizar patrones de tráfico durante el día.
    """
    hours = []
    transactions = []
    
    # Generar datos para las últimas 24 horas
    current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)
    
    for i in range(24):
        hour = current_hour - timedelta(hours=i)
        hours.append(hour.strftime("%H:00"))
        transactions.append(random.randint(50, 250))
    
    # Invertir para mostrar cronológicamente
    hours.reverse()
    transactions.reverse()
    
    return {
        "labels": hours,
        "data": transactions,
        "backgroundColor": "rgba(54, 162, 235, 0.6)",
        "borderColor": "rgba(54, 162, 235, 1)",
        "borderWidth": 2
    }

@router.get("/api/charts/transaction-status", summary="Datos para Gráfico de Estado de Transacciones")
async def get_transaction_status_chart() -> Dict[str, Any]:
    """
    🥧 **API para Gráfico de Estado de Transacciones**
    
    Devuelve datos para generar gráfico de dona con distribución de estados.
    """
    return {
        "labels": ["Completed", "Pending", "Failed", "Cancelled"],
        "data": [
            random.randint(800, 1200),  # Completed (mayoría)
            random.randint(50, 150),    # Pending
            random.randint(10, 50),     # Failed (pocos)
            random.randint(5, 25)       # Cancelled (muy pocos)
        ],
        "backgroundColor": [
            "#28a745",  # Verde para completed
            "#ffc107",  # Amarillo para pending
            "#dc3545",  # Rojo para failed
            "#6c757d"   # Gris para cancelled
        ]
    }

@router.get("/api/charts/volume-trend", summary="Datos para Gráfico de Tendencia de Volumen")
async def get_volume_trend() -> Dict[str, Any]:
    """
    📊 **API para Gráfico de Tendencia de Volumen**
    
    Devuelve datos para generar gráfico de línea con tendencia de volumen diario.
    """
    dates = []
    volumes = []
    
    # Últimos 30 días
    for i in range(30):
        date = datetime.now().date() - timedelta(days=i)
        dates.append(date.strftime("%m/%d"))
        volumes.append(random.randint(100000, 800000))
    
    # Invertir para mostrar cronológicamente
    dates.reverse()
    volumes.reverse()
    
    return {
        "labels": dates,
        "data": volumes,
        "borderColor": "#20c997",
        "backgroundColor": "rgba(32, 201, 151, 0.1)",
        "fill": True
    }

# ================================
# 🔐 PROTECTED ADMIN ENDPOINTS
# ================================

@router.get("/admin/transactions", response_class=HTMLResponse, summary="Panel de Administración de Transacciones")
async def admin_transactions(request: Request):
    """
    🔐 **Panel Administrativo de Transacciones**
    
    Panel administrativo de transacciones para demostración.
    Acceso libre para reclutadores bancarios.
    """
    return templates.TemplateResponse("basic_dashboard.html", {
        "request": request,
        "title": "Transaction Management - NeuroBank Admin"
    })

@router.get("/admin/users", response_class=HTMLResponse, summary="Panel de Administración de Usuarios")
async def admin_users(request: Request):
    """
    👥 **Panel Administrativo de Usuarios**
    
    Panel administrativo de usuarios para demostración.
    Acceso libre para reclutadores bancarios.
    """
    return templates.TemplateResponse("admin_users.html", {
        "request": request,
        "title": "User Management - NeuroBank Admin"
    })

@router.get("/admin/reports", response_class=HTMLResponse, summary="Panel de Reportes Administrativos")
async def admin_reports(request: Request):
    """
    📈 **Panel de Reportes Administrativos**
    
    Panel de reportes financieros para demostración.
    Acceso libre para reclutadores bancarios.
    """
    return templates.TemplateResponse("admin_reports.html", {
        "request": request,
        "title": "Financial Reports - NeuroBank Admin"
    })

# ================================
# 🎯 ENDPOINT INFO
# ================================

@router.get("/info", summary="Información del Backoffice Dashboard")
async def dashboard_info():
    """
    ℹ️ **Información del Dashboard**
    
    Información técnica sobre el backoffice dashboard.
    """
    return {
        "name": "NeuroBank Backoffice Dashboard",
        "version": "1.0.0",
        "description": "Enterprise-grade admin panel para gestión bancaria",
        "features": [
            "Real-time metrics dashboard",
            "Transaction monitoring",
            "System health tracking",
            "Interactive charts",
            "Protected admin panels",
            "Responsive design"
        ],
        "endpoints": {
            "dashboard": "/backoffice/",
            "metrics_api": "/backoffice/api/metrics",
            "transactions_api": "/backoffice/api/transactions",
            "health_api": "/backoffice/api/system-health",
            "admin_panels": [
                "/backoffice/admin/transactions",
                "/backoffice/admin/users", 
                "/backoffice/admin/reports"
            ]
        },
        "tech_stack": [
            "FastAPI",
            "Jinja2 Templates",
            "Chart.js for visualizations",
            "Bootstrap 5 for UI",
            "Real-time data updates"
        ]
    }
