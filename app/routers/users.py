from __future__ import annotations

import uuid as uuid_pkg

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Security, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import require_permissions
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserInDB, UserResponse, UserUpdate
from app.services.user_service import (
    assign_roles,
    create_user,
    delete_user,
    get_user_by_id,
    list_users,
    update_user,
)

router = APIRouter(prefix="/users", tags=["👥 User Management"])

# Evitar B008: crear dependencias como singletons de módulo
db_dep = Depends(get_db)
perm_read = Security(require_permissions(), scopes=["users:read"])
perm_write = Security(require_permissions(), scopes=["users:write"])
perm_delete = Security(require_permissions(), scopes=["users:delete"])


@router.get("/", response_model=list[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = db_dep,
    _current_user: User = perm_read,
) -> list[User]:
    return await list_users(db, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=UserInDB)
async def get_user(
    user_id: str = Path(...),
    db: AsyncSession = db_dep,
    _current_user: User = perm_read,
) -> User:
    user = await get_user_by_id(db, uuid_from_str(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


@router.post("/", response_model=UserResponse, status_code=201)
async def create_user_admin(
    payload: UserCreate,
    db: AsyncSession = db_dep,
    _current_user: User = perm_write,
) -> User:
    return await create_user(db, payload)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user_endpoint(
    user_id: str,
    payload: UserUpdate,
    db: AsyncSession = db_dep,
    _current_user: User = perm_write,
) -> User:
    return await update_user(db, uuid_from_str(user_id), payload)


@router.delete("/{user_id}", status_code=204, response_class=Response, response_model=None)
async def delete_user_endpoint(
    user_id: str,
    db: AsyncSession = db_dep,
    _current_user: User = perm_delete,
) -> None:
    ok = await delete_user(db, uuid_from_str(user_id))
    if not ok:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return Response(status_code=204)


@router.post("/{user_id}/roles", response_model=UserInDB)
async def assign_roles_endpoint(
    user_id: str,
    role_names: list[str],
    db: AsyncSession = db_dep,
    _current_user: User = perm_write,
) -> User:
    return await assign_roles(db, uuid_from_str(user_id), role_names)


def uuid_from_str(value: str) -> uuid_pkg.UUID:
    return uuid_pkg.UUID(value)
