"""
Tests for UserRole CRUD operations and API endpoints
"""
import os
import pytest
from httpx import ASGITransport, AsyncClient

from app.config import get_settings
from app.database import get_db
from app.main import app

# Get API key from settings
settings = get_settings()
TEST_API_KEY = settings.api_key


@pytest.fixture(scope="function")
def test_db():
    """Create a test database for each test"""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from app.database import Base
    
    # Use unique database for each test
    import tempfile
    temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_db.close()
    
    db_url = f"sqlite:///{temp_db.name}"
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    Base.metadata.create_all(bind=engine)
    
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield TestingSessionLocal
    
    # Cleanup
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    os.unlink(temp_db.name)


@pytest.mark.asyncio
async def test_create_role(test_db):
    """Test creating a new role"""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.post(
            "/api/roles",
            json={"name": "admin", "description": "Administrator with full access"},
            headers={"X-API-Key": TEST_API_KEY},
        )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "admin"
    assert data["description"] == "Administrator with full access"
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_create_duplicate_role(test_db):
    """Test creating a role with duplicate name fails"""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        # Create first role
        await ac.post(
            "/api/roles",
            json={"name": "customer", "description": "Customer role"},
            headers={"X-API-Key": TEST_API_KEY},
        )

        # Try to create duplicate
        response = await ac.post(
            "/api/roles",
            json={"name": "customer", "description": "Another customer role"},
            headers={"X-API-Key": TEST_API_KEY},
        )

    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


@pytest.mark.asyncio
async def test_list_roles(test_db):
    """Test listing all roles"""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        # Create some roles
        await ac.post(
            "/api/roles",
            json={"name": "admin", "description": "Admin"},
            headers={"X-API-Key": TEST_API_KEY},
        )
        await ac.post(
            "/api/roles",
            json={"name": "customer", "description": "Customer"},
            headers={"X-API-Key": TEST_API_KEY},
        )

        # List roles
        response = await ac.get("/api/roles", headers={"X-API-Key": TEST_API_KEY})

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert any(role["name"] == "admin" for role in data)
    assert any(role["name"] == "customer" for role in data)


@pytest.mark.asyncio
async def test_get_role_by_id(test_db):
    """Test getting a specific role by ID"""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        # Create a role
        create_response = await ac.post(
            "/api/roles",
            json={"name": "auditor", "description": "Auditor role"},
            headers={"X-API-Key": TEST_API_KEY},
        )
        role_id = create_response.json()["id"]

        # Get the role
        response = await ac.get(
            f"/api/roles/{role_id}", headers={"X-API-Key": TEST_API_KEY}
        )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == role_id
    assert data["name"] == "auditor"


@pytest.mark.asyncio
async def test_get_nonexistent_role(test_db):
    """Test getting a role that doesn't exist"""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get(
            "/api/roles/550e8400-e29b-41d4-a716-446655440000",
            headers={"X-API-Key": TEST_API_KEY},
        )

    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_update_role(test_db):
    """Test updating a role"""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        # Create a role
        create_response = await ac.post(
            "/api/roles",
            json={"name": "manager", "description": "Manager role"},
            headers={"X-API-Key": TEST_API_KEY},
        )
        role_id = create_response.json()["id"]

        # Update the role
        response = await ac.put(
            f"/api/roles/{role_id}",
            json={"description": "Updated manager role"},
            headers={"X-API-Key": TEST_API_KEY},
        )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == role_id
    assert data["name"] == "manager"
    assert data["description"] == "Updated manager role"


@pytest.mark.asyncio
async def test_delete_role(test_db):
    """Test deleting a role"""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        # Create a role
        create_response = await ac.post(
            "/api/roles",
            json={"name": "temp", "description": "Temporary role"},
            headers={"X-API-Key": TEST_API_KEY},
        )
        role_id = create_response.json()["id"]

        # Delete the role
        response = await ac.delete(
            f"/api/roles/{role_id}", headers={"X-API-Key": TEST_API_KEY}
        )

    assert response.status_code == 204

    # Verify role is deleted
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        get_response = await ac.get(
            f"/api/roles/{role_id}", headers={"X-API-Key": TEST_API_KEY}
        )
    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_role_unauthorized_access(test_db):
    """Test accessing role endpoints without API key"""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/api/roles")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_role_invalid_api_key(test_db):
    """Test accessing role endpoints with invalid API key"""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get("/api/roles", headers={"X-API-Key": "invalid-key"})

    assert response.status_code == 403
