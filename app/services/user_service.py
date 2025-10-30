from __future__ import annotations

import uuid as uuid_pkg

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth.password import (
    get_password_hash,
    validate_password_strength,
    verify_password,
)
from app.models import Role, User
from app.schemas import UserCreate, UserUpdate


async def create_user(
    db: AsyncSession, user_data: UserCreate, roles: list[str] | None = None
) -> User:
    is_valid, msg = validate_password_strength(user_data.password)
    if not is_valid:
        raise ValueError(msg)

    hashed = get_password_hash(user_data.password)
    user = User(
        id=uuid_pkg.uuid4(),
        username=user_data.username,
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed,
    )
    if roles:
        stmt_roles = select(Role).where(Role.name.in_(roles))
        res_roles = await db.execute(stmt_roles)
        user.roles = list(res_roles.scalars().all())

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_user_by_id(db: AsyncSession, user_id: uuid_pkg.UUID) -> User | None:
    stmt = (
        select(User)
        .options(selectinload(User.roles).selectinload(Role.permissions))
        .where(User.id == user_id)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    stmt = (
        select(User)
        .options(selectinload(User.roles).selectinload(Role.permissions))
        .where(User.username == username)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_users(
    db: AsyncSession, skip: int = 0, limit: int = 100, is_active: bool | None = None
) -> list[User]:
    stmt = select(User).options(selectinload(User.roles)).offset(skip).limit(limit)
    if is_active is not None:
        stmt = stmt.where(User.is_active == is_active)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update_user(
    db: AsyncSession, user_id: uuid_pkg.UUID, user_data: UserUpdate
) -> User:
    user = await get_user_by_id(db, user_id)
    if not user:
        msg = "User not found"
        raise ValueError(msg)

    if user_data.username is not None:
        user.username = user_data.username
    if user_data.email is not None:
        user.email = user_data.email
    if user_data.full_name is not None:
        user.full_name = user_data.full_name
    if user_data.password is not None:
        is_valid, msg = validate_password_strength(user_data.password)
        if not is_valid:
            raise ValueError(msg)
        user.hashed_password = get_password_hash(user_data.password)

    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user_id: uuid_pkg.UUID) -> bool:
    user = await get_user_by_id(db, user_id)
    if not user:
        return False
    user.is_active = False
    await db.commit()
    return True


async def assign_roles(
    db: AsyncSession, user_id: uuid_pkg.UUID, role_names: list[str]
) -> User:
    user = await get_user_by_id(db, user_id)
    if not user:
        msg = "User not found"
        raise ValueError(msg)
    stmt_roles = select(Role).where(Role.name.in_(role_names))
    res_roles = await db.execute(stmt_roles)
    user.roles = list(res_roles.scalars().all())
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(
    db: AsyncSession, username: str, password: str
) -> User | None:
    user = await get_user_by_username(db, username)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user
