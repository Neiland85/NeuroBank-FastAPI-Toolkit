from __future__ import annotations

import uuid as uuid_pkg
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models import Permission, Role, User
from app.schemas import RoleCreate, RoleUpdate

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


async def create_role(
    db: AsyncSession, role_data: RoleCreate, permissions: list[str] | None = None
) -> Role:
    role = Role(
        id=uuid_pkg.uuid4(), name=role_data.name, description=role_data.description
    )
    if permissions:
        stmt = select(Permission).where(Permission.name.in_(permissions))
        res = await db.execute(stmt)
        role.permissions = list(res.scalars().all())
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return role


async def get_role_by_id(db: AsyncSession, role_id: uuid_pkg.UUID) -> Role | None:
    stmt = (
        select(Role)
        .options(selectinload(Role.permissions), selectinload(Role.users))
        .where(Role.id == role_id)
    )
    res = await db.execute(stmt)
    return res.scalar_one_or_none()


async def get_role_by_name(db: AsyncSession, name: str) -> Role | None:
    stmt = select(Role).where(Role.name == name)
    res = await db.execute(stmt)
    return res.scalar_one_or_none()


async def list_roles(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Role]:
    stmt = select(Role).offset(skip).limit(limit)
    res = await db.execute(stmt)
    return list(res.scalars().all())


async def update_role(
    db: AsyncSession, role_id: uuid_pkg.UUID, role_data: RoleUpdate
) -> Role:
    role = await get_role_by_id(db, role_id)
    if not role:
        msg = "Role not found"
        raise ValueError(msg)
    if role_data.name is not None:
        role.name = role_data.name
    if role_data.description is not None:
        role.description = role_data.description
    await db.commit()
    await db.refresh(role)
    return role


async def delete_role(db: AsyncSession, role_id: uuid_pkg.UUID) -> bool:
    role = await get_role_by_id(db, role_id)
    if not role:
        return False
    if role.name in {"admin", "customer", "auditor"}:
        msg = "System roles cannot be deleted"
        raise ValueError(msg)
    await db.delete(role)
    await db.commit()
    return True


async def assign_permissions(
    db: AsyncSession, role_id: uuid_pkg.UUID, permission_names: list[str]
) -> Role:
    role = await get_role_by_id(db, role_id)
    if not role:
        msg = "Role not found"
        raise ValueError(msg)
    stmt = select(Permission).where(Permission.name.in_(permission_names))
    res = await db.execute(stmt)
    role.permissions = list(res.scalars().all())
    await db.commit()
    await db.refresh(role)
    return role


async def create_permission(
    db: AsyncSession,
    name: str,
    resource: str,
    action: str,
    description: str | None = None,
) -> Permission:
    perm = Permission(
        id=uuid_pkg.uuid4(),
        name=name,
        resource=resource,
        action=action,
        description=description,
    )
    db.add(perm)
    await db.commit()
    await db.refresh(perm)
    return perm


async def list_permissions(db: AsyncSession) -> list[Permission]:
    res = await db.execute(select(Permission))
    return list(res.scalars().all())


async def get_user_permissions(db: AsyncSession, user_id: uuid_pkg.UUID) -> list[str]:
    stmt = (
        select(User)
        .options(selectinload(User.roles).selectinload(Role.permissions))
        .where(User.id == user_id)
    )
    res = await db.execute(stmt)
    user = res.scalar_one_or_none()
    if not user:
        return []
    perms: set[str] = set()
    for r in user.roles:
        for p in r.permissions:
            perms.add(p.name)
    return sorted(perms)


async def initialize_default_roles(db: AsyncSession) -> None:
    # Definir permisos base por recurso
    resources = ["users", "roles", "transactions", "accounts", "reports"]
    actions = ["read", "write", "delete"]
    all_perm_names: list[str] = []
    # Crear permisos si no existen
    for res_name in resources:
        for act in actions:
            perm_name = f"{res_name}:{act}"
            exists = await db.execute(
                select(Permission).where(Permission.name == perm_name)
            )
            if not exists.scalar_one_or_none():
                await create_permission(db, perm_name, res_name, act)
            all_perm_names.append(perm_name)

    # Admin con todos los permisos
    admin = await get_role_by_name(db, "admin")
    if not admin:
        admin = await create_role(
            db, RoleCreate(name="admin", description="System administrator")
        )
        await assign_permissions(db, admin.id, all_perm_names)

    # Customer permisos mínimos (sin acceso a users)
    customer = await get_role_by_name(db, "customer")
    if not customer:
        customer_allowed: list[str] = []
        customer = await create_role(
            db, RoleCreate(name="customer", description="End customer")
        )
        if customer_allowed:
            await assign_permissions(db, customer.id, customer_allowed)

    # Auditor solo lectura
    auditor = await get_role_by_name(db, "auditor")
    if not auditor:
        read_only = [f"{r}:read" for r in resources]
        auditor = await create_role(
            db, RoleCreate(name="auditor", description="Read-only auditor")
        )
        await assign_permissions(db, auditor.id, read_only)

    # Operator con permisos de lectura básicos
    operator = await get_role_by_name(db, "operator")
    if not operator:
        read_only = [f"{r}:read" for r in ["transactions", "accounts"]]
        operator = await create_role(
            db, RoleCreate(name="operator", description="Operations operator")
        )
        await assign_permissions(db, operator.id, read_only)
