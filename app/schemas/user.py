"""
Pydantic schemas for User
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base schema for User"""
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Unique username",
        examples=["john_doe"]
    )
    email: EmailStr = Field(
        ...,
        description="User's email address",
        examples=["john.doe@example.com"]
    )
    full_name: Optional[str] = Field(
        None,
        max_length=100,
        description="Full name of the user",
        examples=["John Doe"]
    )


class UserCreate(UserBase):
    """Schema for creating a new User"""
    password: str = Field(
        ...,
        min_length=8,
        description="User password (will be hashed)",
        examples=["SecurePassword123!"]
    )
    role_id: UUID = Field(
        ...,
        description="ID of the user's role"
    )


class UserUpdate(BaseModel):
    """Schema for updating a User"""
    username: Optional[str] = Field(
        None,
        min_length=3,
        max_length=50,
        description="Unique username"
    )
    email: Optional[EmailStr] = Field(
        None,
        description="User's email address"
    )
    full_name: Optional[str] = Field(
        None,
        max_length=100,
        description="Full name of the user"
    )
    password: Optional[str] = Field(
        None,
        min_length=8,
        description="New password (will be hashed)"
    )
    role_id: Optional[UUID] = Field(
        None,
        description="ID of the user's role"
    )
    is_active: Optional[bool] = Field(
        None,
        description="Whether the user account is active"
    )


class UserResponse(UserBase):
    """Schema for User response"""
    id: UUID = Field(..., description="Unique identifier of the user")
    role_id: UUID = Field(..., description="ID of the user's role")
    is_active: bool = Field(..., description="Whether the user is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "username": "john_doe",
                "email": "john.doe@example.com",
                "full_name": "John Doe",
                "role_id": "660e8400-e29b-41d4-a716-446655440001",
                "is_active": True,
                "created_at": "2025-07-20T15:30:45.123456Z",
                "updated_at": "2025-07-20T15:30:45.123456Z"
            }
        }
    }
