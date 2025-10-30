from __future__ import annotations

import re
import uuid
from datetime import UTC, datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    StrictBool,
    StrictStr,
    ValidationInfo,
    field_validator,
)

# ---------- Permission Schemas ----------


class ORMSchema(BaseModel):
    """Base para respuestas que mapean desde objetos ORM."""

    model_config = ConfigDict(from_attributes=True)


class PermissionBase(BaseModel):
    name: StrictStr = Field(..., description="Nombre del permiso", examples=["read"])
    resource: StrictStr = Field(..., description="Recurso objetivo", examples=["users"])
    action: StrictStr = Field(
        ..., description="Acción permitida", examples=["list", "create"]
    )
    description: StrictStr | None = Field(
        default=None, description="Descripción opcional del permiso"
    )


class PermissionCreate(PermissionBase):
    pass


class PermissionResponse(ORMSchema, PermissionBase):
    id: uuid.UUID


# ---------- Role Schemas ----------


class RoleBase(BaseModel):
    name: StrictStr = Field(..., description="Nombre del rol", examples=["admin"])
    description: StrictStr | None = Field(
        default=None, description="Descripción opcional del rol"
    )


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class RoleResponse(ORMSchema, RoleBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    permissions: list[PermissionResponse] = Field(default_factory=list)

    @field_validator("created_at", "updated_at")
    @classmethod
    def ensure_timezone_aware(cls, value: datetime, _info: ValidationInfo) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value


class RoleWithUsers(RoleResponse):
    users: list[UserResponse] = Field(default_factory=list)


# ---------- User Schemas ----------


class UserBase(BaseModel):
    username: StrictStr = Field(
        ...,
        min_length=3,
        max_length=32,
        pattern=r"^[a-zA-Z0-9_.-]+$",
        description="Nombre de usuario (3-32 chars, letras/números/._-)",
        examples=["john"],
    )
    email: EmailStr = Field(..., description="Correo electrónico válido")
    full_name: StrictStr | None = Field(
        default=None, description="Nombre completo del usuario"
    )


class UserCreate(UserBase):
    password: StrictStr = Field(
        ..., min_length=8, description="Contraseña con mayúsculas, minúsculas y dígito"
    )

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str, _info: ValidationInfo) -> str:
        if (
            not re.search(r"[A-Z]", v)
            or not re.search(r"[a-z]", v)
            or not re.search(r"\d", v)
        ):
            msg = "La contraseña debe incluir mayúsculas, minúsculas y dígitos"
            raise ValueError(msg)
        return v


class UserUpdate(BaseModel):
    username: StrictStr | None = Field(
        default=None,
        min_length=3,
        max_length=32,
        pattern=r"^[a-zA-Z0-9_.-]+$",
        description="Nuevo nombre de usuario",
    )
    email: EmailStr | None = Field(default=None, description="Nuevo correo")
    full_name: StrictStr | None = Field(
        default=None, description="Nuevo nombre completo"
    )
    password: StrictStr | None = Field(
        default=None, min_length=8, description="Nueva contraseña"
    )


class UserInDB(ORMSchema, UserBase):
    id: uuid.UUID
    is_active: StrictBool
    is_superuser: StrictBool
    created_at: datetime
    updated_at: datetime
    roles: list[RoleResponse] = Field(default_factory=list)

    @field_validator("created_at", "updated_at")
    @classmethod
    def ensure_timezone_aware(cls, value: datetime, _info: ValidationInfo) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value


class UserResponse(ORMSchema, UserBase):
    id: uuid.UUID
    is_active: StrictBool
    is_superuser: StrictBool
    created_at: datetime
    updated_at: datetime

    @field_validator("created_at", "updated_at")
    @classmethod
    def ensure_timezone_aware(cls, value: datetime, _info: ValidationInfo) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value


# ---------- Auth Schemas ----------


class Token(BaseModel):
    access_token: StrictStr
    token_type: Literal["bearer"] = "bearer"  # - not a password
    refresh_token: StrictStr | None = None


class TokenData(BaseModel):
    username: StrictStr
    scopes: list[str] = Field(default_factory=list)


class LoginRequest(BaseModel):
    username: StrictStr
    password: StrictStr


class RefreshTokenRequest(BaseModel):
    refresh_token: str
