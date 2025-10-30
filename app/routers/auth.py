from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm  # - used at runtime via factory

from app.auth.dependencies import get_current_user
from app.auth.jwt import create_access_token, create_refresh_token, decode_token
from app.database import get_db
from app.schemas import Token, UserCreate, UserResponse
from app.services.user_service import (
    authenticate_user,
    create_user,
)

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from app.models import User

router = APIRouter(prefix="/auth", tags=["🔐 Authentication"])


# Factory para obtener el formulario OAuth2 en tiempo de ejecución (evita ForwardRef)
def get_oauth2_form():
    from fastapi.security import OAuth2PasswordRequestForm as _Form

    return _Form


# Singletons para evitar B008
db_dep = Depends(get_db)
current_user_dep = Depends(get_current_user)


@router.post("/login", response_model=Token, summary="Iniciar sesión (OAuth2)")
async def login(
    form_data: "OAuth2PasswordRequestForm" = Depends(get_oauth2_form()),  # noqa: UP037
    db: AsyncSession = db_dep,
) -> Token:
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas"
        )
    access = create_access_token(
        {
            "sub": user.username,
            "scopes": [p.name for r in user.roles for p in r.permissions],
        }
    )
    refresh = create_refresh_token(user.username)
    return Token(access_token=access, refresh_token=refresh)


@router.post("/register", response_model=UserResponse, summary="Registro de usuario")
async def register(payload: UserCreate, db: AsyncSession = db_dep) -> User:
    # Delegar en el servicio y manejadores globales para mapear excepciones de dominio
    return await create_user(db, payload, roles=["customer"])


@router.post("/refresh", response_model=Token, summary="Refrescar token de acceso")
async def refresh_token(refresh_token: str) -> Token:
    data = decode_token(refresh_token)
    access = create_access_token({"sub": data.username})
    return Token(access_token=access, refresh_token=refresh_token)


@router.get("/me", response_model=UserResponse, summary="Usuario actual")
async def me(user: User = current_user_dep) -> User:
    return user


@router.post("/logout", summary="Cerrar sesión (placeholder)")
async def logout() -> dict:
    return {"detail": "Logout exitoso (sin blacklist aún)"}
