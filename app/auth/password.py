from __future__ import annotations

import re
from typing import Final

from passlib.context import CryptContext

from app.config import get_settings

settings = get_settings()

# Contexto único para hashing/verificación
# Asegura que settings tenga el atributo con valor por defecto 8
if not hasattr(settings, "min_password_length"):
    settings.min_password_length = 8

MIN_PASSWORD_LENGTH: Final[int] = getattr(settings, "min_password_length", 8)
pwd_context = CryptContext(
    schemes=getattr(settings, "password_hash_schemes", ["argon2", "bcrypt"]),
    deprecated="auto",
)


def _truncate_for_bcrypt(password: str) -> str:
    """Trunca la contraseña a 72 bytes para compatibilidad con bcrypt.

    bcrypt solo procesa los primeros 72 bytes; exceder ese límite provoca errores
    o verificaciones inconsistentes. Esta función mantiene compatibilidad con
    contraseñas largas codificadas en UTF-8.
    """
    password_bytes = password.encode("utf-8")
    return password_bytes[:72].decode("utf-8", errors="ignore")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Si el hash almacenado es bcrypt, trunca antes de verificar
    scheme = pwd_context.identify(hashed_password) or ""
    candidate = (
        _truncate_for_bcrypt(plain_password) if scheme == "bcrypt" else plain_password
    )
    return bool(pwd_context.verify(candidate, hashed_password))


def get_password_hash(password: str) -> str:
    # Si bcrypt está habilitado en los esquemas, trunca antes de hashear para evitar
    # ValueError por contraseñas > 72 bytes y garantizar consistencia con verify.
    configured_schemes = getattr(
        settings, "password_hash_schemes", ["argon2", "bcrypt"]
    )
    password_to_hash = (
        _truncate_for_bcrypt(password) if "bcrypt" in configured_schemes else password
    )
    return str(pwd_context.hash(password_to_hash))


def validate_password_strength(password: str) -> tuple[bool, str]:
    if len(password) < MIN_PASSWORD_LENGTH:
        return (
            False,
            f"La contraseña debe tener al menos {MIN_PASSWORD_LENGTH} caracteres",
        )
    if not re.search(r"[A-Z]", password):
        return False, "La contraseña debe contener al menos una letra mayúscula"  # type: ignore[unreachable]
    if not re.search(r"[a-z]", password):
        return False, "La contraseña debe contener al menos una letra minúscula"  # type: ignore[unreachable]
    if not re.search(r"\d", password):
        return False, "La contraseña debe contener al menos un dígito"  # type: ignore[unreachable]
    return True, ""
