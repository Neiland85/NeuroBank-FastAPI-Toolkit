from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Security, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_permissions
from app.database import get_db
from app.schemas import PermissionResponse, RoleCreate, RoleResponse, RoleUpdate, RoleWithUsers
from app.services.role_service import (
    assign_permissions,
    create_role,
    get_role_by_id,
    list_permissions,
    list_roles,
    update_role,
    delete_role,
)


router = APIRouter(prefix="/roles", tags=["🎭 Role Management"])


@router.get("/", response_model=List[RoleResponse])
async def get_roles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user=Security(require_permissions(), scopes=["roles:read"]),
):
    return await list_roles(db, skip=skip, limit=limit)


@router.get("/{role_id}", response_model=RoleWithUsers)
async def get_role(
    role_id: str, db: AsyncSession = Depends(get_db), current_user=Security(require_permissions(), scopes=["roles:read"])
):
    import uuid as _uuid

    role = await get_role_by_id(db, _uuid.UUID(role_id))
    if not role:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return role


@router.post("/", response_model=RoleResponse, status_code=201)
async def create_role_endpoint(
    payload: RoleCreate, db: AsyncSession = Depends(get_db), current_user=Security(require_permissions(), scopes=["roles:write"])
):
    return await create_role(db, payload)


@router.put("/{role_id}", response_model=RoleResponse)
async def update_role_endpoint(
    role_id: str, payload: RoleUpdate, db: AsyncSession = Depends(get_db), current_user=Security(require_permissions(), scopes=["roles:write"])
):
    import uuid as _uuid

    return await update_role(db, _uuid.UUID(role_id), payload)


@router.delete("/{role_id}", status_code=204)
async def delete_role_endpoint(
    role_id: str, db: AsyncSession = Depends(get_db), current_user=Security(require_permissions(), scopes=["roles:delete"])
):
    import uuid as _uuid

    ok = await delete_role(db, _uuid.UUID(role_id))
    if not ok:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return None


@router.post("/{role_id}/permissions", response_model=RoleResponse)
async def assign_permissions_endpoint(
    role_id: str,
    permission_names: List[str],
    db: AsyncSession = Depends(get_db),
    current_user=Security(require_permissions(), scopes=["roles:write"]),
):
    import uuid as _uuid

    return await assign_permissions(db, _uuid.UUID(role_id), permission_names)


@router.get("/../permissions/", response_model=List[PermissionResponse])
async def get_permissions(
    db: AsyncSession = Depends(get_db), current_user=Security(require_permissions(), scopes=["roles:read"])
):
    return await list_permissions(db)


