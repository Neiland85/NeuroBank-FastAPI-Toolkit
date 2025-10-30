"""
CRUD operations for UserRole
"""
from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.models.role import UserRole
from app.schemas.role import UserRoleCreate, UserRoleUpdate


class RoleCRUD:
    """CRUD operations for UserRole"""
    
    def get(self, db: Session, role_id: UUID) -> Optional[UserRole]:
        """Get a role by ID"""
        return db.query(UserRole).filter(UserRole.id == role_id).first()
    
    def get_by_name(self, db: Session, name: str) -> Optional[UserRole]:
        """Get a role by name"""
        return db.query(UserRole).filter(UserRole.name == name).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[UserRole]:
        """Get all roles with pagination"""
        return db.query(UserRole).offset(skip).limit(limit).all()
    
    def create(self, db: Session, role_in: UserRoleCreate) -> UserRole:
        """Create a new role"""
        db_role = UserRole(
            name=role_in.name,
            description=role_in.description,
        )
        db.add(db_role)
        db.commit()
        db.refresh(db_role)
        return db_role
    
    def update(
        self, db: Session, role_id: UUID, role_in: UserRoleUpdate
    ) -> Optional[UserRole]:
        """Update a role"""
        db_role = self.get(db, role_id)
        if not db_role:
            return None
        
        update_data = role_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_role, field, value)
        
        db.commit()
        db.refresh(db_role)
        return db_role
    
    def delete(self, db: Session, role_id: UUID) -> Optional[UserRole]:
        """Delete a role"""
        db_role = self.get(db, role_id)
        if not db_role:
            return None
        
        db.delete(db_role)
        db.commit()
        return db_role


# Create a singleton instance
role_crud = RoleCRUD()
