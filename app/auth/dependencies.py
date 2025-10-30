import logging

from fastapi import Depends, HTTPException, Request
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordBearer,
    SecurityScopes,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.jwt import decode_token
from app.config import get_settings
from app.database import get_db
from app.models import User
from app.services.user_service import get_user_by_username

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

    # Aceptar API Key por X-API-Key o como Bearer en Authorization (compatibilidad)
    if "x-api-key" in request.headers:
        provided_api_key = request.headers["x-api-key"]
    elif credentials and credentials.credentials:
        provided_api_key = credentials.credentials

    if not provided_api_key:
        raise HTTPException(
            status_code=401,
            detail="API key required. Use header 'X-API-Key: <key>'",
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
    user = await get_user_by_username(db, token_data.username)
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


from collections.abc import Awaitable, Callable


def require_role(role_name: str) -> Callable[..., Awaitable[User]]:
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
    """
    Autenticación flexible que soporta JWT Bearer token o API Key.

    Descripción:
        Intenta autenticar usando un JWT en el header Authorization (Bearer). Si el JWT
        es inválido/expirado o no hay credenciales, realiza un fallback a autenticación
        por API Key (preferentemente desde el header 'X-API-Key'). No lanza excepciones
        en fallos de autenticación esperados; retorna None para permitir lógica de
        fallback en el endpoint.

    Args:
        request: Objeto Request de FastAPI para acceder a headers e IP del cliente.
        credentials: Credenciales Bearer opcionales del header Authorization.
        db: Sesión asíncrona de SQLAlchemy para consultar el usuario.

    Returns:
        User | None: El usuario autenticado si el JWT es válido y el usuario existe.
        None si la autenticación es por API Key o si ambos métodos fallan.

    Notas:
        - Diseñado para endpoints que aceptan JWT y API Key.
        - Las excepciones de autenticación esperadas no se propagan; se registra
          contexto y se retorna None.
        - Errores de BD y fallos inesperados se propagan para manejo global.
    """
    logger = logging.getLogger(__name__)
    # 1) Intentar JWT Bearer si hay credenciales
    if credentials and credentials.scheme and credentials.credentials:
        token_value = credentials.credentials
        try:
            token_data = decode_token(token_value)
            user = await get_user_by_username(db, token_data.username)
            if user:
                return user
            # Usuario no encontrado en BD pero token válido
            logger.warning(
                "JWT válido pero usuario no encontrado en BD",
                extra={
                    "username": token_data.username,
                    "client": request.client.host if request.client else "unknown",
                },
            )
            return None
        except HTTPException as e:
            # Token inválido/expirado/sin subject: esperado en flujo de fallback
            logger.debug(
                "Autenticación JWT fallida, intentando fallback a API Key",
                extra={
                    "detail": getattr(e, "detail", None),
                    "status": getattr(e, "status_code", None),
                    "client": request.client.host if request.client else "unknown",
                },
            )
            return None
        # Nota: Errores de BD (SQLAlchemyError) y otros inesperados se propagan
        # intencionalmente para manejo por el exception handler global.

    # 2) Fallback API Key
    try:
        verify_api_key(request, credentials)
        logger.debug(
            "Autenticación por API Key exitosa",
            extra={
                "client": request.client.host if request.client else "unknown",
            },
        )
        return None
    except HTTPException as e:
        # Ambos métodos de autenticación fallaron
        logger.info(
            "Autenticación flexible fallida: JWT y API Key inválidos",
            extra={
                "detail": getattr(e, "detail", None),
                "client": request.client.host if request.client else "unknown",
            },
        )
        return None
