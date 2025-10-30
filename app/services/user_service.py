from __future__ import annotations

import uuid as uuid_pkg
from typing import TYPE_CHECKING

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.auth.password import (
    get_password_hash,
    validate_password_strength,
    verify_password,
)
from app.models import Role, User
from app.services.errors import (
    EmailExistsError,
    UsernameExistsError,
    UserNotFoundError,
    ValidationError,
    WeakPasswordError,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.schemas import UserCreate, UserUpdate


async def create_user(
    db: AsyncSession, user_data: UserCreate, roles: list[str] | None = None
) -> User:
    """
    Crea un usuario. Valida unicidad de username/email y fortaleza de contraseña.

    Raises
    ------
    UsernameExistsError
        Si el username ya existe.
    EmailExistsError
        Si el email ya existe.
    WeakPasswordError
        Si la contraseña no cumple las políticas.
    ValidationError
        Si ocurre un error de integridad no clasificable.
    """
    # Unicidad
    if await get_user_by_username(db, user_data.username):
        msg = "Username already exists"
        raise UsernameExistsError(msg)
    if await get_user_by_email(db, user_data.email):
        msg = "Email already exists"
        raise EmailExistsError(msg)

    is_valid, msg = validate_password_strength(user_data.password)
    if not is_valid:
        raise WeakPasswordError(msg)

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
        found_roles = list(res_roles.scalars().all())
        requested_names = set(roles)
        found_names = {r.name for r in found_roles}
        missing = sorted(requested_names - found_names)
        if missing:
            msg = f"Roles inexistentes: {', '.join(missing)}"
            raise ValidationError(msg)
        user.roles = found_roles

    db.add(user)
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        message = str(getattr(exc, "orig", exc))
        lower_msg = message.lower()
        if "username" in lower_msg:
            msg = "Username already exists"
            raise UsernameExistsError(msg)
        if "email" in lower_msg:
            msg = "Email already exists"
            raise EmailExistsError(msg)
        msg = "Violación de integridad no clasificable durante creación de usuario"
        raise ValidationError(msg)
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
    # Mantener carga ansiosa como en get_user_by_username
    stmt = (
        select(User)
        .options(selectinload(User.roles).selectinload(Role.permissions))
        .where(User.email == email)
    )
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
    """
    Actualiza datos de un usuario.

    Raises
    ------
    UserNotFoundError
        Si el usuario no existe.
    UsernameExistsError
        Si el nuevo username ya existe.
    EmailExistsError
        Si el nuevo email ya existe.
    WeakPasswordError
        Si la nueva contraseña no cumple las políticas.
    ValidationError
        Si ocurre un error de integridad no clasificable.
    """
    user = await get_user_by_id(db, user_id)
    if not user:
        msg = "User not found"
        raise UserNotFoundError(msg)

    # Unicidad condicional
    if user_data.username is not None and user_data.username != user.username:
        if await get_user_by_username(db, user_data.username):
            msg = "Username already exists"
            raise UsernameExistsError(msg)
    if user_data.email is not None and user_data.email != user.email:
        if await get_user_by_email(db, user_data.email):
            msg = "Email already exists"
            raise EmailExistsError(msg)

    if user_data.username is not None:
        user.username = user_data.username
    if user_data.email is not None:
        user.email = user_data.email
    if user_data.full_name is not None:
        user.full_name = user_data.full_name
    if user_data.password is not None:
        is_valid, msg = validate_password_strength(user_data.password)
        if not is_valid:
            raise WeakPasswordError(msg)
        user.hashed_password = get_password_hash(user_data.password)

    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        message = str(getattr(exc, "orig", exc))
        lower_msg = message.lower()
        if "username" in lower_msg:
            msg = "Username already exists"
            raise UsernameExistsError(msg)
        if "email" in lower_msg:
            msg = "Email already exists"
            raise EmailExistsError(msg)
        msg = "Violación de integridad no clasificable durante actualización de usuario"
        raise ValidationError(msg)
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
    """
    Asigna un conjunto de roles por nombre a un usuario.

    Raises
    ------
    UserNotFoundError
        Si el usuario no existe.
    ValidationError
        Si alguno de los nombres de rol solicitados no existe.
    """
    user = await get_user_by_id(db, user_id)
    if not user:
        msg = "User not found"
        raise UserNotFoundError(msg)
    stmt_roles = select(Role).where(Role.name.in_(role_names))
    res_roles = await db.execute(stmt_roles)
    found_roles = list(res_roles.scalars().all())
    found_names = {r.name for r in found_roles}
    requested_names = set(role_names)
    missing = sorted(requested_names - found_names)
    if missing:
        msg = f"Roles inexistentes: {', '.join(missing)}"
        raise ValidationError(msg)
    user.roles = found_roles
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
