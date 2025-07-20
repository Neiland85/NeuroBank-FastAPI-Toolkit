import uuid
from datetime import datetime
from typing import Dict, Any
from loguru import logger


def generate_invoice(order_id: str) -> Dict[str, Any]:
    """
    Genera la factura de un pedido.
    
    Args:
        order_id (str): ID del pedido para generar la factura
        
    Returns:
        Dict[str, Any]: Datos de la factura generada
        
    Raises:
        ValueError: Si el order_id no es válido
    """
    if not order_id or not order_id.strip():
        logger.error("Order ID cannot be empty or None")
        raise ValueError("Order ID is required")
    
    # Generar ID único de factura
    invoice_id = f"INV-{datetime.now().strftime('%Y-%m')}-{str(uuid.uuid4())[:8].upper()}"
    
    # Fecha actual en formato ISO
    issued_at = datetime.now().strftime('%Y-%m-%d')
    
    # Simular cálculo del monto basado en el order_id
    base_amount = hash(order_id) % 100 + 50.0  # Entre 50-149
    amount = round(base_amount + (base_amount * 0.21), 2)  # IVA incluido
    
    invoice_data = {
        "invoice_id": invoice_id,
        "order_id": order_id,
        "amount": amount,
        "currency": "EUR",
        "issued_at": issued_at,
        "status": "issued",
        "tax_rate": 0.21,
        "subtotal": base_amount,
        "tax_amount": round(base_amount * 0.21, 2)
    }
    
    logger.info(f"Invoice generated: {invoice_id} for order: {order_id}")
    
    # FUTURO: Aquí se integrará con:
    # - Base de datos para persistir la factura
    # - S3 para almacenar PDF de la factura
    # - Sistema de contabilidad externo
    
    return invoice_data
