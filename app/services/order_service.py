from datetime import datetime, timedelta
from typing import Dict, Any
from loguru import logger


def get_order_status(order_id: str) -> Dict[str, Any]:
    """
    Obtiene el estado actual de un pedido.
    
    Args:
        order_id (str): ID único del pedido a consultar
        
    Returns:
        Dict[str, Any]: Estado completo del pedido
        
    Raises:
        ValueError: Si el order_id no es válido
    """
    if not order_id or not order_id.strip():
        logger.error("Order ID cannot be empty or None")
        raise ValueError("Order ID is required")
    
    # Simular diferentes estados basados en el ID
    status_options = ["Pendiente", "En preparación", "En tránsito", "Entregado", "Cancelado"]
    carriers = ["Correos Express", "SEUR", "MRW", "DHL", "Amazon Logistics"]
    
    # Generar estado pseudo-aleatorio basado en el order_id
    status_index = hash(order_id) % len(status_options)
    carrier_index = hash(f"{order_id}_carrier") % len(carriers)
    
    status = status_options[status_index]
    carrier = carriers[carrier_index]
    
    # Calcular ETA dinámicamente
    if status == "Entregado":
        eta = "Entregado"
    elif status == "Cancelado":
        eta = "N/A"
    else:
        days_to_add = (hash(order_id) % 5) + 1  # 1-5 días
        eta_date = datetime.now() + timedelta(days=days_to_add)
        eta = eta_date.strftime('%Y-%m-%d')
    
    order_data = {
        "order_id": order_id,
        "status": status,
        "carrier": carrier,
        "eta": eta,
        "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "tracking_number": f"TRK{hash(order_id) % 1000000:06d}",
        "estimated_delivery_time": "08:00-18:00" if status not in ["Entregado", "Cancelado"] else None
    }
    
    logger.info(f"Order status retrieved: {order_id} - Status: {status}")
    
    # FUTURO: Aquí se integrará con:
    # - Base de datos de pedidos
    # - APIs de transportistas reales
    # - Sistema de tracking en tiempo real
    
    return order_data
