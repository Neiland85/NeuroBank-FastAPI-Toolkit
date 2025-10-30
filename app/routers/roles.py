"""
API routes for UserRole management
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.dependencies import verify_api_key
from app.crud.role import role_crud
from app.database import get_db
from app.schemas.role import UserRoleCreate, UserRoleResponse, UserRoleUpdate

router = APIRouter(
    prefix="/roles",
    tags=["👥 User Role Management"],
    dependencies=[Depends(verify_api_key)],
    responses={
        401: {"description": "API Key missing or invalid"},
        404: {"description": "Role not found"},
        500: {"description": "Internal server error"},
    },
)


@router.get(
    "",
    response_model=List[UserRoleResponse],
    summary="📋 List All Roles",
    description="""
    **Retrieve all user roles in the system**
    
    Returns a list of all available user roles with pagination support.
    
    ### 🔍 Use Cases:
    - View all available roles for user assignment
    - Role management and administration
    - System configuration verification
    
    ### 🔐 Authentication:
    Requires valid API Key in the header.
    """,
)
async def list_roles(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """
    **List all user roles**
    
    Retrieves all roles with optional pagination parameters.
    """
    roles = role_crud.get_all(db, skip=skip, limit=limit)
    return roles


@router.post(
    "",
    response_model=UserRoleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="➕ Create New Role",
    description="""
    **Create a new user role**
    
    Creates a new role in the system with a unique name and description.
    
    ### 📋 Requirements:
    - Role name must be unique
    - Name must be 1-50 characters
    - Description is optional (max 255 characters)
    
    ### 🔐 Authentication:
    Requires valid API Key in the header.
    """,
)
async def create_role(
    role_in: UserRoleCreate,
    db: Session = Depends(get_db),
):
    """
    **Create a new role**
    
    Creates a role with the provided name and description.
    """
    # Check if role with this name already exists
    existing_role = role_crud.get_by_name(db, name=role_in.name)
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role with name '{role_in.name}' already exists"
        )
    
    role = role_crud.create(db, role_in=role_in)
    return role


@router.get(
    "/{role_id}",
    response_model=UserRoleResponse,
    summary="🔍 Get Role by ID",
    description="""
    **Retrieve a specific user role**
    
    Returns detailed information about a role identified by its UUID.
    
    ### 🔐 Authentication:
    Requires valid API Key in the header.
    """,
)
async def get_role(
    role_id: UUID,
    db: Session = Depends(get_db),
):
    """
    **Get role by ID**
    
    Retrieves a role by its unique identifier.
    """
    role = role_crud.get(db, role_id=role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with id '{role_id}' not found"
        )
    return role


@router.put(
    "/{role_id}",
    response_model=UserRoleResponse,
    summary="✏️ Update Role",
    description="""
    **Update an existing user role**
    
    Updates role information such as name or description.
    
    ### 📋 Notes:
    - Only provided fields will be updated
    - Role name must remain unique if changed
    
    ### 🔐 Authentication:
    Requires valid API Key in the header.
    """,
)
async def update_role(
    role_id: UUID,
    role_in: UserRoleUpdate,
    db: Session = Depends(get_db),
):
    """
    **Update role**
    
    Updates the specified role with new information.
    """
    # If updating name, check if new name is already taken
    if role_in.name:
        existing_role = role_crud.get_by_name(db, name=role_in.name)
        if existing_role and existing_role.id != role_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role with name '{role_in.name}' already exists"
            )
    
    role = role_crud.update(db, role_id=role_id, role_in=role_in)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with id '{role_id}' not found"
        )
    return role


@router.delete(
    "/{role_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="🗑️ Delete Role",
    description="""
    **Delete a user role**
    
    Permanently removes a role from the system.
    
    ### ⚠️ Warning:
    - This operation cannot be undone
    - Users with this role should be reassigned first
    
    ### 🔐 Authentication:
    Requires valid API Key in the header.
    """,
)
async def delete_role(
    role_id: UUID,
    db: Session = Depends(get_db),
):
    """
    **Delete role**
    
    Removes the specified role from the system.
    """
    role = role_crud.delete(db, role_id=role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with id '{role_id}' not found"
        )
    return None
