"""
UserRole model for role-based access control
"""
import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class UserRole(Base):
    """
    User role model for managing user permissions
    
    Attributes:
        id: Unique identifier for the role (UUID)
        name: Unique name of the role (e.g., 'admin', 'customer', 'auditor')
        description: Human-readable description of the role
        created_at: Timestamp when the role was created
        updated_at: Timestamp when the role was last updated
    """
    __tablename__ = "user_roles"
    
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False,
        index=True,
    )
    name = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )
    description = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
    
    # Relationship to users
    users = relationship("User", back_populates="role")
    
    def __repr__(self) -> str:
        return f"<UserRole(name='{self.name}', description='{self.description}')>"
