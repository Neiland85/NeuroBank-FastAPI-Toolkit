def get_order_status(order_id: str) -> dict:
    """
    Obtiene el estado de un pedido.
    Por ahora es mock; conecta aquí tu BBDD o servicio externo.
    """
    # TODO: Lógica real
    return {
        "order_id": order_id,
        "status": "En tránsito",
        "carrier": "Correos Express",
        "eta": "2025-07-25"
    }
