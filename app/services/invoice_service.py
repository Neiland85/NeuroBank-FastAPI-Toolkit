def generate_invoice(order_id: str) -> dict:
    """
    **Servicio para generar facturas de órdenes bancarias**

    Por ahora es mock; persiste en base de datos o S3 cuando lo implementes.
    En producción, aquí irían las integraciones con sistemas contables.
    """
    # TODO: Implementar lógica real con persistencia
    # Simulación de respuesta realista para testing
    return {
        "invoice_id": f"INV-2025-{hash(order_id) % 999999:06d}",
        "order_id": order_id,
        "amount": 1250.75,
        "currency": "EUR",
        "issued_at": "2025-07-20T15:45:30Z",
    }
