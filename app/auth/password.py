from __future__ import annotations

import re
from typing import Final

from passlib.context import CryptContext

from app.config import get_settings

settings = get_settings()

# Contexto único para hashing/verificación
MIN_PASSWORD_LENGTH: Final[int] = 8
pwd_context = CryptContext(
    schemes=settings.__dict__.get("password_hash_schemes", ["argon2", "bcrypt"]),
    deprecated="auto",
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bool(pwd_context.verify(plain_password, hashed_password))


def get_password_hash(password: str) -> str:
    return str(pwd_context.hash(password))


def validate_password_strength(password: str) -> tuple[bool, str]:
    if len(password) < MIN_PASSWORD_LENGTH:
        return False, "La contraseña debe tener al menos 8 caracteres"
    if not re.search(r"[A-Z]", password):
        return False, "La contraseña debe contener al menos una letra mayúscula"  # type: ignore[unreachable]
    if not re.search(r"[a-z]", password):
        return False, "La contraseña debe contener al menos una letra minúscula"  # type: ignore[unreachable]
    if not re.search(r"\d", password):
        return False, "La contraseña debe contener al menos un dígito"  # type: ignore[unreachable]
    return True, ""
