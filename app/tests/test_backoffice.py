"""Tests for Backoffice API endpoints.

These tests verify that all documented backoffice endpoints are functional
and match the specifications in HOTFIX_PR_DESCRIPTION.md.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_backoffice_api_metrics():
    """Test /backoffice/api/metrics endpoint returns valid dashboard metrics."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/backoffice/api/metrics")

    assert response.status_code == 200
    data = response.json()
    
    # Verify required metrics fields
    assert "total_transactions" in data
    assert "total_volume" in data
    assert "active_accounts" in data
    assert "success_rate" in data
    assert "avg_response_time" in data
    assert "api_calls_today" in data
    
    # Verify data types
    assert isinstance(data["total_transactions"], int)
    assert isinstance(data["total_volume"], (int, float, str))
    assert isinstance(data["active_accounts"], int)
    assert isinstance(data["success_rate"], (int, float))
    assert isinstance(data["avg_response_time"], (int, float))
    assert isinstance(data["api_calls_today"], int)


@pytest.mark.asyncio
async def test_backoffice_api_transactions_search_default():
    """Test /backoffice/api/transactions/search endpoint with default parameters."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/backoffice/api/transactions/search")

    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert "transactions" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "total_pages" in data
    
    # Verify pagination
    assert isinstance(data["page"], int)
    assert isinstance(data["page_size"], int)
    assert isinstance(data["total"], int)
    assert isinstance(data["total_pages"], int)
    assert isinstance(data["transactions"], list)
    
    # Verify transaction structure if any exist
    if data["transactions"]:
        tx = data["transactions"][0]
        assert "id" in tx
        assert "reference" in tx
        assert "amount" in tx
        assert "currency" in tx
        assert "status" in tx
        assert "type" in tx
        assert "created_at" in tx


@pytest.mark.asyncio
async def test_backoffice_api_transactions_search_with_pagination():
    """Test transactions search with custom pagination parameters."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get(
            "/backoffice/api/transactions/search",
            params={"page": 2, "page_size": 10}
        )

    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 2
    assert data["page_size"] == 10


@pytest.mark.asyncio
async def test_backoffice_api_transactions_search_with_filters():
    """Test transactions search with query and filter parameters."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get(
            "/backoffice/api/transactions/search",
            params={
                "query": "test",
                "status": "completed",
                "transaction_type": "transfer"
            }
        )

    assert response.status_code == 200
    data = response.json()
    assert "transactions" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_backoffice_api_system_health():
    """Test /backoffice/api/system-health endpoint."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/backoffice/api/system-health")

    assert response.status_code == 200
    data = response.json()
    
    # Verify required health fields
    assert "status" in data
    assert "database" in data
    assert "api_gateway" in data
    assert "cache" in data
    assert "uptime" in data
    assert "last_check" in data
    assert "response_time" in data
    
    # Verify status is healthy
    assert data["status"] == "healthy"
    assert data["database"] == "online"
    assert data["api_gateway"] == "operational"
    assert data["cache"] == "active"


@pytest.mark.asyncio
async def test_backoffice_info_endpoint():
    """Test /backoffice/info endpoint returns system information."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/backoffice/info")

    assert response.status_code == 200
    data = response.json()
    
    # Verify info structure
    assert "name" in data
    assert "version" in data
    assert "description" in data
    assert "features" in data
    assert "endpoints" in data
    assert "tech_stack" in data
    
    # Verify endpoints structure
    assert "dashboard" in data["endpoints"]
    assert "metrics_api" in data["endpoints"]
    assert "transactions_api" in data["endpoints"]
    assert "health_api" in data["endpoints"]
    assert "admin_panels" in data["endpoints"]


@pytest.mark.asyncio
async def test_backoffice_dashboard_home_accessible():
    """Test /backoffice/ dashboard is accessible."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/backoffice/")

    # Should return HTML response (200 or redirect)
    assert response.status_code in [200, 302, 307]

