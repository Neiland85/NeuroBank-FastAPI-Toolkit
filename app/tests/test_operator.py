import pytest
import os
from httpx import AsyncClient, ASGITransport
from app.main import app

# Configurar API key para tests - usando variable de entorno
TEST_API_KEY = "test_secure_key_for_testing_only_not_production"
os.environ["API_KEY"] = TEST_API_KEY

@pytest.mark.asyncio
async def test_order_status():
    """Test del endpoint de consulta de estado de orden"""
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as ac:
        resp = await ac.get(
            "/operator/order_status/ORD-2025-001234",
            headers={"X-API-Key": TEST_API_KEY}
        )
    
    assert resp.status_code == 200
    data = resp.json()
    assert data["order_id"] == "ORD-2025-001234"
    assert data["status"] == "processing"
    assert data["carrier"] == "VISA_NETWORK"
    assert "eta" in data

@pytest.mark.asyncio
async def test_generate_invoice():
    """Test del endpoint de generación de facturas"""
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as ac:
        resp = await ac.post(
            "/operator/generate_invoice",
            json={"order_id": "ORD-2025-001234"},
            headers={"X-API-Key": TEST_API_KEY}
        )
    
    assert resp.status_code == 200
    data = resp.json()
    assert data["order_id"] == "ORD-2025-001234"
    assert "invoice_id" in data
    assert abs(data["amount"] - 1250.75) < 0.01  # Comparación de float segura
    assert data["currency"] == "EUR"
    assert "issued_at" in data

@pytest.mark.asyncio
async def test_order_status_with_bearer_token():
    """Test del endpoint usando Bearer token authentication"""
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as ac:
        resp = await ac.get(
            "/operator/order_status/ORD-2025-001234",
            headers={"Authorization": f"Bearer {TEST_API_KEY}"}
        )
    
    assert resp.status_code == 200
    data = resp.json()
    assert data["order_id"] == "ORD-2025-001234"

@pytest.mark.asyncio
async def test_order_status_unauthorized():
    """Test de autenticación fallida - sin API key"""
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as ac:
        resp = await ac.get("/operator/order_status/ORD-2025-001234")
    
    assert resp.status_code == 401
    data = resp.json()
    assert "API key required" in data["detail"]

@pytest.mark.asyncio
async def test_order_status_forbidden():
    """Test de autenticación fallida - API key incorrecta"""
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as ac:
        resp = await ac.get(
            "/operator/order_status/ORD-2025-001234",
            headers={"X-API-Key": "wrong-api-key"}
        )
    
    assert resp.status_code == 403
    data = resp.json()
    assert "Invalid API key" in data["detail"]
