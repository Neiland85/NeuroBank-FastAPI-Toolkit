import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.mark.asyncio
async def test_health_check():
    """Test del endpoint de health check"""
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as ac:
        response = await ac.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data
    assert "version" in data
    assert "timestamp" in data
    assert "environment" in data
    assert data["service"] == "NeuroBank FastAPI Toolkit"
    assert data["version"] == "1.0.0"

@pytest.mark.asyncio
async def test_root_endpoint():
    """Test del endpoint raíz con información completa"""
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test"
    ) as ac:
        response = await ac.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert data["status"] == "operational"
    assert "documentation" in data
    assert data["documentation"]["swagger_ui"] == "/docs"
    assert data["documentation"]["redoc"] == "/redoc" 
    assert "endpoints" in data
    assert "features" in data
    assert len(data["features"]) >= 4  # Debe tener al menos 4 características
    assert data["version"] == "1.0.0"
