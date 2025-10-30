"""
User model with role-based access control
"""
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    """
    User model with role-based permissions
    
    Attributes:
        id: Unique identifier for the user (UUID)
        username: Unique username
        email: Unique email address
        hashed_password: Hashed password for authentication
        full_name: Full name of the user
        role_id: Foreign key to UserRole
        is_active: Whether the user account is active
        created_at: Timestamp when the user was created
        updated_at: Timestamp when the user was last updated
    """
    __tablename__ = "users"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
        index=True,
    )
    username = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )
    email = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    role_id = Column(
        UUID(as_uuid=True),
        ForeignKey("user_roles.id"),
        nullable=False,
    )
    is_active = Column(String(10), default="true", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    
    # Relationship to role
    role = relationship("UserRole", back_populates="users")
    
    def __repr__(self) -> str:
        return f"<User(username='{self.username}', email='{self.email}')>"
