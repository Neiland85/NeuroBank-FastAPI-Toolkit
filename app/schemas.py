from __future__ import annotations

import re
from typing import TYPE_CHECKING

from pydantic import BaseModel, EmailStr, Field, ValidationInfo, field_validator

if TYPE_CHECKING:
    import uuid
    from datetime import datetime

# ---------- Permission Schemas ----------


class PermissionBase(BaseModel):
    name: str
    resource: str
    action: str
    description: str | None = None


class PermissionCreate(PermissionBase):
    pass


class PermissionResponse(PermissionBase):
    id: uuid.UUID

    class Config:
        from_attributes = True


# ---------- Role Schemas ----------


class RoleBase(BaseModel):
    name: str
    description: str | None = None


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class RoleResponse(RoleBase):
    id: uuid.UUID
    created_at: datetime
    permissions: list[PermissionResponse] = []

    class Config:
        from_attributes = True


class RoleWithUsers(RoleResponse):
    users: list[UserResponse] = []


# ---------- User Schemas ----------


class UserBase(BaseModel):
    username: str = Field(..., examples=["john"])
    email: EmailStr
    full_name: str | None = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

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
    username: str | None = None
    email: EmailStr | None = None
    full_name: str | None = None
    password: str | None = Field(default=None, min_length=8)


class UserInDB(UserBase):
    id: uuid.UUID
    is_active: bool
    is_superuser: bool
    created_at: datetime
    roles: list[RoleResponse] = []

    class Config:
        from_attributes = True


class UserResponse(UserBase):
    id: uuid.UUID
    is_active: bool
    is_superuser: bool

    class Config:
        from_attributes = True


# ---------- Auth Schemas ----------


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str | None = None


class TokenData(BaseModel):
    username: str
    scopes: list[str] = []


class LoginRequest(BaseModel):
    username: str
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str
