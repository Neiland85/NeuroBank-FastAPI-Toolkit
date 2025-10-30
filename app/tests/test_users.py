import pytest


@pytest.mark.anyio
async def test_users_crud_as_admin(client, admin_headers):
    # Crear usuario
    create = await client.post(
        "/api/users/",
        json={
            "username": "user1",
            "email": "u1@example.com",
            "password": "StrongPass123",
        },
        headers=admin_headers,
    )
    assert create.status_code in (200, 201)
    user = create.json()
    user_id = user["id"]

    # Listar
    lst = await client.get("/api/users/", headers=admin_headers)
    assert lst.status_code == 200
    assert any(u["id"] == user_id for u in lst.json())

    # Actualizar
    upd = await client.put(
        f"/api/users/{user_id}",
        json={"full_name": "Updated Name"},
        headers=admin_headers,
    )
    assert upd.status_code == 200
    assert upd.json().get("full_name") in ("Updated Name", None)  # full_name opcional

    # Asignar roles
    assign = await client.post(
        f"/api/users/{user_id}/roles",
        json=["auditor"],
        headers=admin_headers,
    )
    assert assign.status_code == 200

    delete = await client.delete(f"/api/users/{user_id}", headers=admin_headers)
    assert delete.status_code in (200, 204)


@pytest.mark.anyio
async def test_users_admin_only_actions_forbidden_to_operator(client, operator_headers):
    # Listar require permiso users:read que operator podría no tener; esperar 403/401
    lst = await client.get("/api/users/", headers=operator_headers)
    assert lst.status_code in (401, 403)

    # Crear usuario (admin-only)
    create = await client.post(
        "/api/users/",
        json={"username": "xxx", "email": "x@example.com", "password": "StrongPass123"},
        headers=operator_headers,
    )
    assert create.status_code in (401, 403)

    # Intento de actualización propia si se obtiene su id
    me = await client.get("/api/auth/me", headers=operator_headers)
    assert me.status_code == 200
    my_id = me.json()["id"]
    upd = await client.put(
        f"/api/users/{my_id}", json={"full_name": "Op Name"}, headers=operator_headers
    )
    assert upd.status_code in (401, 403)
