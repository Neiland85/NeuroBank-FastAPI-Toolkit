"""
CRUD operations for User
"""
from typing import List, Optional
from uuid import UUID

from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserCRUD:
    """CRUD operations for User"""
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get(self, db: Session, user_id: UUID) -> Optional[User]:
        """Get a user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        """Get a user by username"""
        return db.query(User).filter(User.username == username).first()
    
    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get a user by email"""
        return db.query(User).filter(User.email == email).first()
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination"""
        return db.query(User).offset(skip).limit(limit).all()
    
    def create(self, db: Session, user_in: UserCreate) -> User:
        """Create a new user"""
        db_user = User(
            username=user_in.username,
            email=user_in.email,
            hashed_password=self.get_password_hash(user_in.password),
            full_name=user_in.full_name,
            role_id=user_in.role_id,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    def update(
        self, db: Session, user_id: UUID, user_in: UserUpdate
    ) -> Optional[User]:
        """Update a user"""
        db_user = self.get(db, user_id)
        if not db_user:
            return None
        
        update_data = user_in.model_dump(exclude_unset=True)
        
        # Hash password if it's being updated
        if "password" in update_data:
            update_data["hashed_password"] = self.get_password_hash(update_data["password"])
            del update_data["password"]
        
        # Convert is_active boolean to string for database
        if "is_active" in update_data:
            update_data["is_active"] = "true" if update_data["is_active"] else "false"
        
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db.commit()
        db.refresh(db_user)
        return db_user
    
    def delete(self, db: Session, user_id: UUID) -> Optional[User]:
        """Delete a user"""
        db_user = self.get(db, user_id)
        if not db_user:
            return None
        
        db.delete(db_user)
        db.commit()
        return db_user


# Create a singleton instance
user_crud = UserCRUD()
