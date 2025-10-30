from fastapi import Depends, HTTPException, Request
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordBearer,
    SecurityScopes,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import decode_token
from app.config import get_settings
from app.database import get_db
from app.models import User

# Esquemas de seguridad
security = HTTPBearer(auto_error=False)
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login",
    scopes={
        "users:read": "Leer usuarios",
        "users:write": "Crear/editar usuarios",
        "users:delete": "Eliminar usuarios",
        "roles:read": "Leer roles",
        "roles:write": "Crear/editar roles",
    },
)


def get_api_key() -> str:
    settings = get_settings()
    if not settings.api_key:
        msg = "API_KEY environment variable is required"
        raise ValueError(msg)
    return settings.api_key


def verify_api_key(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> str:
    expected_api_key = get_api_key()
    provided_api_key = None

    if credentials and credentials.credentials:
        provided_api_key = credentials.credentials
    elif "x-api-key" in request.headers:
        provided_api_key = request.headers["x-api-key"]

    if not provided_api_key:
        raise HTTPException(
            status_code=401,
            detail="API key required. Use 'Authorization: Bearer <key>' or 'X-API-Key: <key>'",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if provided_api_key != expected_api_key:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return provided_api_key


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    token_data = decode_token(token)
    stmt = select(User).where(User.username == token_data.username)
    result = await db.execute(stmt)
    user: User | None = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def require_role(role_name: str):
    async def _checker(current_user: User = Depends(get_current_active_user)) -> User:
        if not any(r.name == role_name for r in current_user.roles):
            raise HTTPException(status_code=403, detail="Insufficient role")
        return current_user

    return _checker


def require_permissions():
    async def _checker(
        security_scopes: SecurityScopes,
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        requested = set(security_scopes.scopes or [])
        owned: set[str] = set()
        for role in current_user.roles:
            for perm in role.permissions:
                owned.add(perm.name)

        if not requested.issubset(owned):
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return current_user

    return _checker


async def get_current_user_flexible(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    # 1) Intentar JWT Bearer si hay credenciales
    if credentials and credentials.scheme and credentials.credentials:
        token_value = credentials.credentials
        try:
            token_data = decode_token(token_value)
            stmt = select(User).where(User.username == token_data.username)
            result = await db.execute(stmt)
            user = result.scalar_one_or_none()
            if user:
                return user
        except Exception:
            return None

    # 2) Fallback API Key
    try:
        verify_api_key(request, credentials)
        return None
    except HTTPException:
        return None
