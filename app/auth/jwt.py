from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import cast

import jwt
from fastapi import HTTPException, status

from app.config import get_settings
from app.schemas import TokenData

settings = get_settings()


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
    return cast(
        str,
        jwt.encode(
            to_encode,
            settings.jwt_secret_key or "dev-insecure",
            algorithm=settings.jwt_algorithm,
        ),
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
    return cast(
        str,
        jwt.encode(
            payload,
            settings.jwt_secret_key or "dev-insecure",
            algorithm=settings.jwt_algorithm,
        ),
    )


def decode_token(token: str) -> TokenData:
    try:
        decoded = jwt.decode(
            token,
            settings.jwt_secret_key or "dev-insecure",
            algorithms=[settings.jwt_algorithm],
            audience="neurobank-clients",
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


def get_token_expiry(token: str) -> datetime:
    decoded = jwt.decode(
        token,
        settings.jwt_secret_key or "dev-insecure",
        algorithms=[settings.jwt_algorithm],
        options={"verify_signature": False},
    )
    exp = decoded.get("exp")
    return datetime.fromtimestamp(exp, tz=UTC)
