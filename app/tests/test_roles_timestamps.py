import pytest

from app.database import AsyncSessionLocal
from app.services.user_service import assign_roles, get_user_by_username


def _is_tz_aware(ts: str) -> bool:
    return ts.endswith(("Z", "+00:00")) or "+" in ts or "-" in ts[-6:]


@pytest.mark.anyio
async def test_roles_list_returns_utc_timestamps(client):
    # Crear usuario básico (customer)
    await client.post(
        "/api/auth/register",
        json={
            "username": "roleviewer",
            "email": "roleviewer@example.com",
            "password": "SecurePass123",
        },
    )
    # Elevar a admin para tener permisos roles:read
    async with AsyncSessionLocal() as db:
        user = await get_user_by_username(db, "roleviewer")
        assert user is not None
        await assign_roles(db, user.id, ["admin"])

    # Login y obtener token con permisos
    login = await client.post(
        "/api/auth/login",
        data={"username": "roleviewer", "password": "SecurePass123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]

    # Listar roles
    resp = await client.get("/api/roles/", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    roles = resp.json()
    assert isinstance(roles, list)
    assert len(roles) >= 1
    for role in roles:
        assert "created_at" in role
        assert isinstance(role["created_at"], str)
        assert "updated_at" in role
        assert isinstance(role["updated_at"], str)
        assert _is_tz_aware(role["created_at"])  # ISO-8601 con zona horaria
        assert _is_tz_aware(role["updated_at"])  # ISO-8601 con zona horaria


@pytest.mark.anyio
async def test_role_detail_returns_utc_timestamps_and_users_have_utc(client):
    # Reutilizar usuario admin de la prueba anterior o crearlo si hace falta
    await client.post(
        "/api/auth/register",
        json={
            "username": "roleviewer2",
            "email": "roleviewer2@example.com",
            "password": "SecurePass123",
        },
    )
    # Elevar a admin para permisos roles:read
    async with AsyncSessionLocal() as db:
        user = await get_user_by_username(db, "roleviewer2")
        assert user is not None
        await assign_roles(db, user.id, ["admin"])

    login = await client.post(
        "/api/auth/login",
        data={"username": "roleviewer2", "password": "SecurePass123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]

    # Obtener lista de roles para elegir uno existente
    resp = await client.get("/api/roles/", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    roles = resp.json()
    assert roles
    role_id = roles[0]["id"]

    # Obtener detalle del rol
    detail = await client.get(
        f"/api/roles/{role_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert detail.status_code == 200
    data = detail.json()
    assert _is_tz_aware(data["created_at"]) and _is_tz_aware(data["updated_at"])

    # Si hay usuarios asociados, sus timestamps deben ser aware
    users = data.get("users", [])
    for u in users:
        assert _is_tz_aware(u["created_at"]) and _is_tz_aware(u["updated_at"])
