"""
Banking operations API router.

Exposes secured endpoints for order status queries and invoice generation.
"""

from fastapi import APIRouter, Depends, Path, status
from pydantic import BaseModel, Field

from app.auth.dependencies import verify_api_key
from app.services.invoice_service import generate_invoice
from app.services.order_service import get_order_status


router = APIRouter(
    prefix="/api",
    tags=["Banking Operations"],
    responses={
        401: {"description": "API Key missing or invalid"},
        404: {"description": "Resource not found"},
        500: {"description": "Internal server error"},
    },
)

# -------------------------------------------------------------------
# Pydantic models
# -------------------------------------------------------------------


class OrderStatusResponse(BaseModel):
    """Response containing the current status of a banking order."""

    order_id: str = Field(..., examples=["ORD-2025-001234"])
    status: str = Field(..., examples=["processing"])
    carrier: str = Field(..., examples=["VISA_NETWORK"])
    eta: str = Field(..., examples=["2025-07-20T16:30:00Z"])

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
    """Request payload for invoice generation."""

    order_id: str = Field(
        ...,
        min_length=5,
        max_length=50,
        examples=["ORD-2025-001234"],
    )


class InvoiceResponse(BaseModel):
    """Response containing generated invoice details."""

    invoice_id: str = Field(..., examples=["INV-2025-789012"])
    order_id: str = Field(..., examples=["ORD-2025-001234"])
    amount: float = Field(..., ge=0, examples=[1250.75])
    currency: str = Field(..., max_length=3, examples=["EUR"])
    issued_at: str = Field(..., examples=["2025-07-20T15:45:30Z"])

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


# -------------------------------------------------------------------
# Endpoints
# -------------------------------------------------------------------


@router.get(
    "/order/{order_id}",
    response_model=OrderStatusResponse,
    summary="Get order status",
    dependencies=[Depends(verify_api_key)],
)
async def order_status(
    order_id: str = Path(
        ...,
        pattern="^[A-Z]{3}-[0-9]{4}-[0-9]{6}$",
        examples=["ORD-2025-001234"],
    ),
) -> OrderStatusResponse:
    """Return the current processing status of an order."""
    return get_order_status(order_id)


@router.post(
    "/invoice",
    response_model=InvoiceResponse,
    summary="Generate invoice",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_api_key)],
)
async def create_invoice(
    data: InvoiceRequest,
) -> InvoiceResponse:
    """Generate an invoice for a completed order."""
    return generate_invoice(data.order_id)
