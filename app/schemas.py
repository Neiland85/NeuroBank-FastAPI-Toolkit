from __future__ import annotations

import re
import uuid
from datetime import datetime, timedelta
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, ValidationInfo, field_validator


# ---------- Permission Schemas ----------


class PermissionBase(BaseModel):
    name: str
    resource: str
    action: str
    description: Optional[str] = None


class PermissionCreate(PermissionBase):
    pass


class PermissionResponse(PermissionBase):
    id: uuid.UUID

    class Config:
        from_attributes = True


# ---------- Role Schemas ----------


class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class RoleResponse(RoleBase):
    id: uuid.UUID
    created_at: datetime
    permissions: List[PermissionResponse] = []

    class Config:
        from_attributes = True


class RoleWithUsers(RoleResponse):
    users: List["UserResponse"] = []


# ---------- User Schemas ----------


class UserBase(BaseModel):
    username: str = Field(..., examples=["john"])
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str, info: ValidationInfo) -> str:
        if not re.search(r"[A-Z]", v) or not re.search(r"[a-z]", v) or not re.search(r"\d", v):
            raise ValueError("La contraseña debe incluir mayúsculas, minúsculas y dígitos")
        return v


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(default=None, min_length=8)


class UserInDB(UserBase):
    id: uuid.UUID
    is_active: bool
    is_superuser: bool
    created_at: datetime
    roles: List[RoleResponse] = []

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
    refresh_token: Optional[str] = None


class TokenData(BaseModel):
    username: str
    scopes: List[str] = []


class LoginRequest(BaseModel):
    username: str
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


