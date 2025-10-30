import pytest


@pytest.mark.anyio
async def test_duplicate_registration_rejected(client):
    payload = {
        "username": "dupuser",
        "email": "dup@example.com",
        "password": "SecurePass123",
    }
    r1 = await client.post("/api/auth/register", json=payload)
    assert r1.status_code in (200, 201)
    r2 = await client.post("/api/auth/register", json=payload)
    # Conflicto por unicidad debe ser 409
    assert r2.status_code == 409


@pytest.mark.anyio
async def test_login_failure_wrong_password(client):
    await client.post(
        "/api/auth/register",
        json={
            "username": "wrongpass",
            "email": "wrong@example.com",
            "password": "RightPass123",
        },
    )
    r = await client.post(
        "/api/auth/login",
        data={"username": "wrongpass", "password": "BadPass"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert r.status_code in (400, 401)


@pytest.mark.anyio
async def test_me_returns_current_user_when_authenticated(client):
    await client.post(
        "/api/auth/register",
        json={
            "username": "meuser",
            "email": "me@example.com",
            "password": "SecurePass123",
        },
    )
    login = await client.post(
        "/api/auth/login",
        data={"username": "meuser", "password": "SecurePass123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    me = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["username"] == "meuser"


@pytest.mark.anyio
async def test_refresh_token_generates_new_access_token(client):
    await client.post(
        "/api/auth/register",
        json={
            "username": "ref",
            "email": "ref@example.com",
            "password": "SecurePass123",
        },
    )
    login = await client.post(
        "/api/auth/login",
        data={"username": "ref", "password": "SecurePass123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login.status_code == 200
    data = login.json()
    refresh = data["refresh_token"]
    r = await client.post("/api/auth/refresh", params={"refresh_token": refresh})
    assert r.status_code == 200
    new_access = r.json()["access_token"]
    assert isinstance(new_access, str)
    assert len(new_access) > 0


@pytest.mark.anyio
async def test_access_token_cannot_be_used_as_refresh(client):
    await client.post(
        "/api/auth/register",
        json={
            "username": "norefresh",
            "email": "norefresh@example.com",
            "password": "SecurePass123",
        },
    )
    login = await client.post(
        "/api/auth/login",
        data={"username": "norefresh", "password": "SecurePass123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login.status_code == 200
    access = login.json()["access_token"]
    r = await client.post("/api/auth/refresh", params={"refresh_token": access})
    assert r.status_code in (400, 401)


@pytest.mark.anyio
async def test_api_key_in_authorization_is_rejected(client):
    # Enviar API key vía Authorization debe ser rechazado con 401
    r = await client.get(
        "/api/order/ORD-2025-001234",
        headers={"Authorization": "Bearer some_api_key_value"},
    )
    assert r.status_code == 401
    detail = r.json().get("detail", "")
    assert "X-API-Key" in detail


@pytest.mark.anyio
async def test_missing_jwt_secret_returns_500_on_login(client, monkeypatch):
    # Forzar ausencia de secreto JWT y verificar error claro en login
    import app.auth.jwt as jwt_mod

    monkeypatch.setattr(jwt_mod.settings, "jwt_secret_key", None, raising=True)

    # Crear usuario primero
    await client.post(
        "/api/auth/register",
        json={
            "username": "nojwt",
            "email": "nojwt@example.com",
            "password": "SecurePass123",
        },
    )
    resp = await client.post(
        "/api/auth/login",
        data={"username": "nojwt", "password": "SecurePass123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert resp.status_code >= 500
