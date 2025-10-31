from fastapi import APIRouter, Depends, Path
from pydantic import BaseModel, Field

from ..auth.dependencies import verify_api_key
from ..services.invoice_service import generate_invoice
from ..services.order_service import get_order_status

# Router con documentación mejorada
router = APIRouter(
    prefix="",
    tags=["🏦 Banking Operations"],
    responses={
        401: {"description": "API Key missing or invalid"},
        404: {"description": "Resource not found"},
        500: {"description": "Internal server error"},
    },
)

# ----- Modelos Pydantic con documentación mejorada -----


class OrderStatusResponse(BaseModel):
    """
    **Respuesta del estado de una orden bancaria**

    Contiene información completa sobre el estado actual de una transacción.
    """

    order_id: str = Field(
        ..., description="Identificador único de la orden", examples=["ORD-2025-001234"]
    )
    status: str = Field(
        ..., description="Estado actual de la orden", examples=["processing"]
    )
    carrier: str = Field(
        ...,
        description="Entidad procesadora de la transacción",
        examples=["VISA_NETWORK"],
    )
    eta: str = Field(
        ...,
        description="Tiempo estimado de finalización (ISO 8601)",
        examples=["2025-07-20T16:30:00Z"],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "order_id": "ORD-2025-001234",
                "status": "processing",
                "carrier": "VISA_NETWORK",
                "eta": "2025-07-20T16:30:00Z",
            }
        }
    }


class InvoiceRequest(BaseModel):
    """
    **Solicitud para generar factura**

    Datos necesarios para generar una factura de transacción bancaria.
    """

    order_id: str = Field(
        ...,
        description="ID de la orden para la cual generar la factura",
        examples=["ORD-2025-001234"],
        min_length=5,
        max_length=50,
    )

    model_config = {"json_schema_extra": {"example": {"order_id": "ORD-2025-001234"}}}


class InvoiceResponse(BaseModel):
    """
    **Respuesta de factura generada**

    Contiene los detalles completos de la factura generada.
    """

    invoice_id: str = Field(
        ...,
        description="Identificador único de la factura generada",
        examples=["INV-2025-789012"],
    )
    order_id: str = Field(
        ..., description="ID de la orden asociada", examples=["ORD-2025-001234"]
    )
    amount: float = Field(
        ..., description="Monto total de la factura", examples=[1250.75], ge=0
    )
    currency: str = Field(
        ..., description="Código de moneda ISO 4217", examples=["EUR"], max_length=3
    )
    issued_at: str = Field(
        ...,
        description="Fecha y hora de emisión (ISO 8601)",
        examples=["2025-07-20T15:45:30Z"],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "invoice_id": "INV-2025-789012",
                "order_id": "ORD-2025-001234",
                "amount": 1250.75,
                "currency": "EUR",
                "issued_at": "2025-07-20T15:45:30Z",
            }
        }
    }


# ----- Endpoints con documentación completa -----


@router.get(
    "/order/{order_id}",
    response_model=OrderStatusResponse,
    summary="📊 Consultar Estado de Orden",
    description="""
    **Consulta el estado actual de una orden bancaria**

    Este endpoint permite verificar el estado de procesamiento de cualquier
    transacción bancaria utilizando su identificador único.

    ### 🔍 Casos de uso:
    - Seguimiento de transferencias en tiempo real
    - Verificación de estado de pagos
    - Monitoreo de transacciones pendientes
    - Auditoría de operaciones bancarias

    ### 📋 Estados posibles:
    - `pending`: Orden recibida, esperando procesamiento
    - `processing`: Transacción en curso
    - `completed`: Operación finalizada exitosamente
    - `failed`: Error en el procesamiento
    - `cancelled`: Orden cancelada por el usuario

    ### 🔐 Autenticación:
    Requiere API Key válida en el header `X-API-Key`.
    """,
    dependencies=[Depends(verify_api_key)],
    responses={
        200: {
            "description": "Estado de orden obtenido exitosamente",
            "content": {
                "application/json": {
                    "examples": {
                        "processing_order": {
                            "summary": "Orden en procesamiento",
                            "value": {
                                "order_id": "ORD-2025-001234",
                                "status": "processing",
                                "carrier": "VISA_NETWORK",
                                "eta": "2025-07-20T16:30:00Z",
                            },
                        },
                        "completed_order": {
                            "summary": "Orden completada",
                            "value": {
                                "order_id": "ORD-2025-005678",
                                "status": "completed",
                                "carrier": "MASTERCARD_NETWORK",
                                "eta": "2025-07-20T15:45:00Z",
                            },
                        },
                    }
                }
            },
        },
        404: {
            "description": "Orden no encontrada",
            "content": {
                "application/json": {
                    "example": {"detail": "Order ORD-2025-999999 not found"}
                }
            },
        },
    },
)
async def order_status(
    order_id: str = Path(
        ...,
        description="Identificador único de la orden a consultar",
        examples=["ORD-2025-001234"],
        pattern="^[A-Z]{3}-[0-9]{4}-[0-9]{6}$",
    )
):
    """
    **Endpoint para consultar el estado de una orden bancaria**

    Procesa la consulta de estado y retorna información detallada
    sobre el procesamiento actual de la transacción.
    """
    return get_order_status(order_id)


@router.post(
    "/invoice/{invoice_id}",
    response_model=InvoiceResponse,
    summary="🧾 Generar Factura",
    description="""
    **Genera una factura oficial para una orden completada**

    Este endpoint crea una factura detallada para una transacción bancaria
    específica, incluyendo todos los datos fiscales requeridos.

    ### 📋 Características:
    - Generación automática de ID de factura
    - Cálculo de montos con precisión decimal
    - Timestamp de emisión en formato ISO 8601
    - Cumplimiento con normativas fiscales europeas

    ### 💼 Casos de uso:
    - Facturación automática post-transacción
    - Generación de comprobantes para auditorías
    - Documentación fiscal de operaciones
    - Integración con sistemas contables

    ### ⚠️ Restricciones:
    - Solo se pueden facturar órdenes con estado `completed`
    - Una orden puede tener múltiples facturas (refacturación)
    - Los montos se calculan incluyendo comisiones aplicables

    ### 🔐 Autenticación:
    Requiere API Key válida en el header `X-API-Key`.
    """,
    dependencies=[Depends(verify_api_key)],
    responses={
        200: {
            "description": "Factura generada exitosamente",
            "content": {
                "application/json": {
                    "examples": {
                        "standard_invoice": {
                            "summary": "Factura estándar",
                            "value": {
                                "invoice_id": "INV-2025-789012",
                                "order_id": "ORD-2025-001234",
                                "amount": 1250.75,
                                "currency": "EUR",
                                "issued_at": "2025-07-20T15:45:30Z",
                            },
                        },
                        "high_amount_invoice": {
                            "summary": "Factura de alto importe",
                            "value": {
                                "invoice_id": "INV-2025-789013",
                                "order_id": "ORD-2025-005678",
                                "amount": 50000.00,
                                "currency": "USD",
                                "issued_at": "2025-07-20T15:50:15Z",
                            },
                        },
                    }
                }
            },
        },
        404: {
            "description": "Orden no encontrada",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Order ORD-2025-999999 not found or not eligible for invoicing"
                    }
                }
            },
        },
    },
)
async def invoice(
    invoice_id: str = Path(
        ..., description="ID de la factura a generar", examples=["INV-2025-789012"]
    ),
    data: InvoiceRequest = None,
):
    """
    **Endpoint para generar facturas de órdenes bancarias**

    Procesa la solicitud de facturación y genera un documento oficial
    con todos los detalles fiscales requeridos.
    """
    return generate_invoice(data.order_id)
