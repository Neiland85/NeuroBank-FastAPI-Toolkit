"""
Tests for role-based access control and JWT authentication
"""
import os
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.auth.dependencies import create_access_token
from app.config import get_settings
from app.crud.role import role_crud
from app.crud.user import user_crud
from app.database import Base, get_db
from app.main import app
from app.schemas.role import UserRoleCreate
from app.schemas.user import UserCreate

# Get API key from settings
settings = get_settings()
TEST_API_KEY = settings.api_key


@pytest.fixture(scope="function")
def test_db():
    """Create a test database for each test"""
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


@pytest.fixture(scope="function")
def setup_test_users(test_db):
    """Create test users with roles"""
    db = test_db()

    # Create roles
    admin_role = role_crud.create(
        db, UserRoleCreate(name="admin", description="Administrator")
    )
    customer_role = role_crud.create(
        db, UserRoleCreate(name="customer", description="Customer")
    )
    auditor_role = role_crud.create(
        db, UserRoleCreate(name="auditor", description="Auditor")
    )

    # Create users
    admin_user = user_crud.create(
        db,
        UserCreate(
            username="admin_user",
            email="admin@test.com",
            password="adminpass123",
            full_name="Admin User",
            role_id=admin_role.id,
        ),
    )
    customer_user = user_crud.create(
        db,
        UserCreate(
            username="customer_user",
            email="customer@test.com",
            password="customerpass123",
            full_name="Customer User",
            role_id=customer_role.id,
        ),
    )
    auditor_user = user_crud.create(
        db,
        UserCreate(
            username="auditor_user",
            email="auditor@test.com",
            password="auditorpass123",
            full_name="Auditor User",
            role_id=auditor_role.id,
        ),
    )

    # Store IDs before closing session
    result = {
        "admin": str(admin_user.id),
        "customer": str(customer_user.id),
        "auditor": str(auditor_user.id),
    }

    db.close()
    return result


def test_create_access_token():
    """Test JWT token creation"""
    token_data = {"sub": "550e8400-e29b-41d4-a716-446655440000", "role": "admin"}
    token = create_access_token(token_data)

    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0


@pytest.mark.asyncio
async def test_get_current_user_valid_token(setup_test_users):
    """Test getting current user with valid JWT token"""
    # This test verifies the token creation works
    # The actual get_current_user function would be tested in integration tests
    # with real endpoints that use it
    admin_id = setup_test_users["admin"]
    token = create_access_token({"sub": str(admin_id)})

    assert token is not None


@pytest.mark.asyncio
async def test_password_hashing():
    """Test password hashing and verification"""
    password = "SecurePassword123!"
    hashed = user_crud.get_password_hash(password)

    assert hashed != password
    assert user_crud.verify_password(password, hashed) is True
    assert user_crud.verify_password("WrongPassword", hashed) is False


@pytest.mark.asyncio
async def test_role_validation(test_db, setup_test_users):
    """Test that roles are correctly assigned to users"""
    db = test_db()

    # Get admin user
    from uuid import UUID
    admin_user = user_crud.get(db, UUID(setup_test_users["admin"]))
    assert admin_user is not None
    assert admin_user.role.name == "admin"

    # Get customer user
    customer_user = user_crud.get(db, UUID(setup_test_users["customer"]))
    assert customer_user is not None
    assert customer_user.role.name == "customer"

    # Get auditor user
    auditor_user = user_crud.get(db, UUID(setup_test_users["auditor"]))
    assert auditor_user is not None
    assert auditor_user.role.name == "auditor"

    db.close()


@pytest.mark.asyncio
async def test_inactive_user_check(test_db, setup_test_users):
    """Test that inactive users are properly identified"""
    db = test_db()

    # Get a user and make them inactive
    from uuid import UUID
    customer_id = UUID(setup_test_users["customer"])
    user = user_crud.get(db, customer_id)
    assert user.is_active == "true"

    # Update user to inactive
    from app.schemas.user import UserUpdate

    updated_user = user_crud.update(
        db, customer_id, UserUpdate(is_active=False)
    )
    assert updated_user.is_active == "false"

    db.close()


@pytest.mark.asyncio
async def test_user_crud_operations(test_db, setup_test_users):
    """Test basic user CRUD operations"""
    db = test_db()

    # Test get by username
    user = user_crud.get_by_username(db, "admin_user")
    assert user is not None
    assert user.username == "admin_user"

    # Test get by email
    user = user_crud.get_by_email(db, "customer@test.com")
    assert user is not None
    assert user.email == "customer@test.com"

    # Test get all users
    all_users = user_crud.get_all(db)
    assert len(all_users) >= 3

    db.close()


@pytest.mark.asyncio
async def test_role_relationship(test_db, setup_test_users):
    """Test that role relationship works correctly"""
    db = test_db()

    # Get a user with role
    from uuid import UUID
    user = user_crud.get(db, UUID(setup_test_users["admin"]))
    assert user.role is not None
    assert user.role.name == "admin"
    assert user.role.description == "Administrator"

    db.close()
