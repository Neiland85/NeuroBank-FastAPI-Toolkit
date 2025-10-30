import pytest

from app.schemas import UserCreate
from app.services.errors import ValidationError
from app.database import AsyncSessionLocal
from app.services.user_service import create_user


@pytest.mark.anyio
async def test_create_user_with_nonexistent_role_raises_validation_error():
    async with AsyncSessionLocal() as db:
        payload = UserCreate(
            username="nouserrole",
            email="nouserrole@example.com",
            password="StrongPass123!",
            full_name=None,
        )
        with pytest.raises(ValidationError) as excinfo:
            await create_user(db, payload, roles=["rol_que_no_existe"])
        # Mensaje debe coincidir con el formato de assign_roles
        assert "Roles inexistentes:" in str(excinfo.value)
        assert "rol_que_no_existe" in str(excinfo.value)


