def generate_invoice(order_id: str) -> dict:
    """
    Genera la factura de un pedido.
    Por ahora es mock; persiste en BBDD o S3 cuando lo implementes.
    """
    # TODO: Lógica real
    return {
        "invoice_id": "INV-2025-0001",
        "order_id": order_id,
        "amount": 149.99,
        "currency": "EUR",
        "issued_at": "2025-07-20"
    }
