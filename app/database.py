"""
Database configuration and session management for NeuroBank FastAPI Toolkit
"""
import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

# Database URL from environment variable
# Default to SQLite for development/testing
DATABASE_URL = os.getenv(
    "DATABASE_URL", "sqlite:///./neurobank.db"
)

# Create SQLAlchemy engine
# For SQLite, we need to enable check_same_thread=False for FastAPI compatibility
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,  # Enable connection health checks
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for declarative models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency for FastAPI
    
    Yields a database session and ensures it's properly closed after use.
    
    Usage:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database tables
    
    Creates all tables defined in models.
    Should be called on application startup.
    """
    # Import all models here to ensure they are registered with Base
    from app.models import user, role  # noqa: F401
    
    Base.metadata.create_all(bind=engine)
