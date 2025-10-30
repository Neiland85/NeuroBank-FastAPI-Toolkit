import asyncio
import os
import pytest
from httpx import AsyncClient
from fastapi import FastAPI
import pathlib

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"

from app.main import app  # noqa: E402
from app.database import init_db, AsyncSessionLocal  # noqa: E402
from app.services.role_service import initialize_default_roles  # noqa: E402
from app.services.user_service import create_user, authenticate_user  # noqa: E402
from app.schemas import UserCreate  # noqa: E402


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    # Limpiar archivo sqlite si existe; la app manejará init vía lifespan
    db_path = pathlib.Path("test.db")
    if db_path.exists():
        db_path.unlink()
    # Crear tablas para asegurar disponibilidad antes del primer request
    asyncio.run(init_db())
    # Sembrar roles por defecto
    async def _seed():
        async with AsyncSessionLocal() as db:
            await initialize_default_roles(db)
    asyncio.run(_seed())
    yield


@pytest.fixture()
async def client():
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c


async def _ensure_user_with_roles(username: str, email: str, password: str, roles: list[str]):
    async with AsyncSessionLocal() as db:
        payload = UserCreate(username=username, email=email, password=password, full_name=None)
        try:
            await create_user(db, payload, roles=roles)
        except Exception:
            # Ignorar si ya existe
            pass


async def _login_get_token(client: AsyncClient, username: str, password: str) -> str:
    resp = await client.post(
        "/api/auth/login",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code == 200
    return resp.json()["access_token"]


@pytest.fixture()
async def admin_headers(client: AsyncClient):
    username, email, password = "admin_user", "admin@example.com", "AdminPass123!"
    await _ensure_user_with_roles(username, email, password, roles=["admin"])
    token = await _login_get_token(client, username, password)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
async def auditor_headers(client: AsyncClient):
    username, email, password = "auditor_user", "auditor@example.com", "AuditorPass123!"
    await _ensure_user_with_roles(username, email, password, roles=["auditor"])
    token = await _login_get_token(client, username, password)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
async def operator_headers(client: AsyncClient):
    username, email, password = "operator_user", "operator@example.com", "OperatorPass123!"
    await _ensure_user_with_roles(username, email, password, roles=["customer", "operator"])  # si existe
    token = await _login_get_token(client, username, password)
    return {"Authorization": f"Bearer {token}"}


