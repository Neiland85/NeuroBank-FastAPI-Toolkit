from __future__ import annotations


class UserNotFoundError(Exception):
    """Se lanza cuando un usuario no existe."""


class UsernameExistsError(Exception):
    """Se lanza cuando el username ya existe."""


class EmailExistsError(Exception):
    """Se lanza cuando el email ya existe."""


class WeakPasswordError(Exception):
    """Se lanza cuando la contraseña no cumple las políticas de seguridad."""


class ValidationError(Exception):
    """Excepción de validación genérica para errores no categorizables."""
