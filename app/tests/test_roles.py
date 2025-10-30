import pytest


@pytest.mark.anyio
async def test_roles_admin_crud_and_permissions(client, admin_headers):
    # Listar roles
    lst = await client.get("/api/roles/", headers=admin_headers)
    assert lst.status_code == 200
    lst.json()

    # Crear rol
    create = await client.post(
        "/api/roles/",
        json={"name": "reviewer", "description": "Can review items"},
        headers=admin_headers,
    )
    assert create.status_code in (200, 201)
    role = create.json()
    role_id = role["id"]

    # Asignar permiso al rol por nombre
    assign = await client.post(
        f"/api/roles/{role_id}/permissions",
        json=["users:read"],
        headers=admin_headers,
    )
    assert assign.status_code == 200


@pytest.mark.anyio
async def test_roles_management_forbidden_to_non_admin(client, operator_headers):
    r = await client.get("/api/roles/", headers=operator_headers)
    assert r.status_code in (401, 403)
    c = await client.post(
        "/api/roles/",
        json={"name": "x", "description": "y"},
        headers=operator_headers,
    )
    assert c.status_code in (401, 403)
