from typing import Final

from passlib.hash import bcrypt as bcrypt_hasher

MAX_BCRYPT_LENGTH: Final[int] = 72


def hash_password(password: str) -> str:
    if password is None:
        raise ValueError("password must not be None")
    # Bcrypt acepta solo los primeros 72 bytes; truncamos de forma explícita
    safe = password[:MAX_BCRYPT_LENGTH]
    return bcrypt_hasher.hash(safe)


def verify_password(password: str, hashed: str) -> bool:
    if password is None or hashed is None:
        return False
    safe = password[:MAX_BCRYPT_LENGTH]
    return bcrypt_hasher.verify(safe, hashed)
