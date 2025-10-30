from __future__ import annotations

from datetime import UTC, datetime, timedelta

import jwt
from fastapi import HTTPException, status

from app.config import get_settings
from app.schemas import TokenData

settings = get_settings()


MAX_JWT_BYTES = 8 * 1024  # 8 KB límite defensivo para tokens


def _ensure_reasonable_size(token: str) -> None:
    if len(token.encode("utf-8")) > MAX_JWT_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="JWT demasiado grande",
        )


def _get_secret() -> str:
    """Obtiene el secreto JWT desde Settings. Falla si no está configurado (excepto tests).

    En tests/CI `Settings` ya auto-provee un secreto.
    """
    if settings.jwt_secret_key:
        return settings.jwt_secret_key
    # En entornos de test, Settings.__init__ configura un secreto temporal
    # Si llega aquí, es una mala configuración en runtime => HTTP 500
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="JWT secret key is not configured",
    )


def _now() -> datetime:
    return datetime.now(UTC)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = _now() + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode.update(
        {
            "exp": expire,
            "iat": _now(),
            "nbf": _now(),
            "iss": "neurobank",
            "aud": "neurobank-clients",
        }
    )
    secret_key = _get_secret()
    return jwt.encode(
        to_encode,
        secret_key,
        algorithm=settings.jwt_algorithm,
    )


def create_refresh_token(username: str) -> str:
    expire = _now() + timedelta(days=settings.refresh_token_expire_days)
    payload = {
        "sub": username,
        "type": "refresh",
        "exp": expire,
        "iat": _now(),
        "nbf": _now(),
        "iss": "neurobank",
        "aud": "neurobank-clients",
    }
    secret_key = _get_secret()
    return jwt.encode(
        payload,
        secret_key,
        algorithm=settings.jwt_algorithm,
    )


def decode_token(token: str) -> TokenData:
    _ensure_reasonable_size(token)
    try:
        decoded = jwt.decode(
            token,
            _get_secret(),
            algorithms=[settings.jwt_algorithm],
            audience="neurobank-clients",
            issuer="neurobank",
            options={"require": ["exp", "iat", "nbf", "iss", "aud"]},
        )
        username = decoded.get("sub") or decoded.get("username")
        scopes = decoded.get("scopes", [])
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: sin sujeto",
            )
        return TokenData(username=username, scopes=scopes)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expirado"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido"
        )


def decode_refresh_token(token: str) -> TokenData:
    """Decodifica y valida que el token sea de tipo refresh."""
    _ensure_reasonable_size(token)
    try:
        decoded = jwt.decode(
            token,
            _get_secret(),
            algorithms=[settings.jwt_algorithm],
            audience="neurobank-clients",
            issuer="neurobank",
            options={"require": ["exp", "iat", "nbf", "iss", "aud"]},
        )
        if decoded.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token no es de tipo refresh",
            )
        username = decoded.get("sub") or decoded.get("username")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: sin sujeto",
            )
        return TokenData(username=username)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expirado"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido"
        )


def get_token_expiry(token: str) -> datetime:
    decoded = jwt.decode(
        token,
        _get_secret(),
        algorithms=[settings.jwt_algorithm],
        options={"verify_signature": False},
    )
    exp = decoded.get("exp")
    return datetime.fromtimestamp(exp, tz=UTC)
