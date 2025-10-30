from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import create_access_token, create_refresh_token, decode_token
from app.auth.password import get_password_hash
from app.database import get_db
from app.schemas import LoginRequest, Token, UserCreate, UserResponse
from app.services.user_service import authenticate_user, create_user, get_user_by_username
from app.auth.dependencies import get_current_user


router = APIRouter(prefix="/auth", tags=["🔐 Authentication"])


@router.post("/login", response_model=Token, summary="Iniciar sesión (OAuth2)")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales inválidas")
    access = create_access_token({"sub": user.username, "scopes": [p.name for r in user.roles for p in r.permissions]})
    refresh = create_refresh_token(user.username)
    return Token(access_token=access, refresh_token=refresh)


@router.post("/register", response_model=UserResponse, summary="Registro de usuario")
async def register(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    # Unicidad de username/email
    if await get_user_by_username(db, payload.username):
        raise HTTPException(status_code=400, detail="El nombre de usuario ya existe")
    user = await create_user(db, payload, roles=["customer"])
    return user


@router.post("/refresh", response_model=Token, summary="Refrescar token de acceso")
async def refresh_token(refresh_token: str, db: AsyncSession = Depends(get_db)):
    data = decode_token(refresh_token)
    access = create_access_token({"sub": data.username})
    return Token(access_token=access, refresh_token=refresh_token)


@router.get("/me", response_model=UserResponse, summary="Usuario actual")
async def me(user=Depends(get_current_user)):
    return user


@router.post("/logout", summary="Cerrar sesión (placeholder)")
async def logout():
    return {"detail": "Logout exitoso (sin blacklist aún)"}


