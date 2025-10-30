"""
Pydantic schemas for UserRole
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class UserRoleBase(BaseModel):
    """Base schema for UserRole"""
    name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Unique name of the role",
        examples=["admin", "customer", "auditor"]
    )
    description: Optional[str] = Field(
        None,
        max_length=255,
        description="Description of the role",
        examples=["Administrator with full access"]
    )


class UserRoleCreate(UserRoleBase):
    """Schema for creating a new UserRole"""
    pass


class UserRoleUpdate(BaseModel):
    """Schema for updating a UserRole"""
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50,
        description="Unique name of the role"
    )
    description: Optional[str] = Field(
        None,
        max_length=255,
        description="Description of the role"
    )


class UserRoleResponse(UserRoleBase):
    """Schema for UserRole response"""
    id: UUID = Field(..., description="Unique identifier of the role")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "admin",
                "description": "Administrator with full access",
                "created_at": "2025-07-20T15:30:45.123456Z",
                "updated_at": "2025-07-20T15:30:45.123456Z"
            }
        }
    }
