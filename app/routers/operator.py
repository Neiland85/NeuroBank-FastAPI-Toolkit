from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from ..services.order_service import get_order_status
from ..services.invoice_service import generate_invoice
from ..auth.dependencies import verify_api_key

router = APIRouter()

# ----- Modelos Pydantic -----
class OrderStatusResponse(BaseModel):
    order_id: str
    status: str
    carrier: str
    eta: str
    last_updated: str
    tracking_number: str
    estimated_delivery_time: str | None

class InvoiceRequest(BaseModel):
    order_id: str

class InvoiceResponse(BaseModel):
    invoice_id: str
    order_id: str
    amount: float
    currency: str
    issued_at: str
    status: str
    tax_rate: float
    subtotal: float
    tax_amount: float

# ----- Endpoints -----
@router.get(
    "/order_status/{order_id}",
    response_model=OrderStatusResponse,
    dependencies=[Depends(verify_api_key)]
)
async def order_status(order_id: str):
    return get_order_status(order_id)

@router.post(
    "/generate_invoice",
    response_model=InvoiceResponse,
    dependencies=[Depends(verify_api_key)]
)
async def invoice(data: InvoiceRequest):
    return generate_invoice(data.order_id)
