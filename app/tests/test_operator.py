import pytest
import os
from httpx import AsyncClient
from app.main import app

# Configurar API key para tests
API_KEY = "test-api-key"
os.environ["API_KEY"] = API_KEY

@pytest.mark.asyncio
async def test_order_status():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.get(
            "/operator/order_status/123",
            headers={"Authorization": f"Bearer {API_KEY}"}
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["order_id"] == "123"

@pytest.mark.asyncio
async def test_generate_invoice():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        resp = await ac.post(
            "/operator/generate_invoice",
            json={"order_id": "123"},
            headers={"Authorization": f"Bearer {API_KEY}"}
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["order_id"] == "123"
