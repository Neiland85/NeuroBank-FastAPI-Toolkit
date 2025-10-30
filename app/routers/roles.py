from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, HTTPException, Query, Response, Security

from app.auth.dependencies import require_permissions
from app.database import get_db
from app.schemas import (
    PermissionResponse,
    RoleCreate,
    RoleResponse,
    RoleUpdate,
    RoleWithUsers,
)
from app.services.role_service import (
    assign_permissions,
    create_role,
    delete_role,
    get_role_by_id,
    list_permissions,
    list_roles,
    update_role,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.models import Permission, Role, User

router = APIRouter(prefix="/roles", tags=["🎭 Role Management"])

# Singletons de dependencies para evitar B008
db_dep = Depends(get_db)
perm_read = Security(require_permissions(), scopes=["roles:read"])
perm_write = Security(require_permissions(), scopes=["roles:write"])
perm_delete = Security(require_permissions(), scopes=["roles:delete"])


@router.get("/", response_model=list[RoleResponse])
async def get_roles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = db_dep,
    _current_user: User = perm_read,
) -> list[Role]:
    return await list_roles(db, skip=skip, limit=limit)


@router.get("/{role_id}", response_model=RoleWithUsers)
async def get_role(
    role_id: str,
    db: AsyncSession = db_dep,
    _current_user: User = perm_read,
) -> Role:
    role = await get_role_by_id(db, uuid.UUID(role_id))
    if not role:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return role


@router.post("/", response_model=RoleResponse, status_code=201)
async def create_role_endpoint(
    payload: RoleCreate,
    db: AsyncSession = db_dep,
    _current_user: User = perm_write,
) -> Role:
    return await create_role(db, payload)


@router.put("/{role_id}", response_model=RoleResponse)
async def update_role_endpoint(
    role_id: str,
    payload: RoleUpdate,
    db: AsyncSession = db_dep,
    _current_user: User = perm_write,
) -> Role:
    return await update_role(db, uuid.UUID(role_id), payload)


@router.delete(
    "/{role_id}", status_code=204, response_class=Response, response_model=None
)
async def delete_role_endpoint(
    role_id: str,
    db: AsyncSession = db_dep,
    _current_user: User = perm_delete,
) -> None:
    ok = await delete_role(db, uuid.UUID(role_id))
    if not ok:
        raise HTTPException(status_code=404, detail="Rol no encontrado")


@router.post("/{role_id}/permissions", response_model=RoleResponse)
async def assign_permissions_endpoint(
    role_id: str,
    permission_names: list[str],
    db: AsyncSession = db_dep,
    _current_user: User = perm_write,
) -> Role:
    return await assign_permissions(db, uuid.UUID(role_id), permission_names)


@router.get("/permissions/", response_model=list[PermissionResponse])
async def get_permissions(
    db: AsyncSession = db_dep,
    _current_user: User = perm_read,
) -> list[Permission]:
    return await list_permissions(db)
