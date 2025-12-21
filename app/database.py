"""
Database Configuration
======================

SQLAlchemy database session management for ZeroSite

Author: ZeroSite Backend Team
Date: 2025-12-17
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

# Database URL (SQLite default, override with env)
DATABASE_URL = getattr(settings, 'database_url', 'sqlite:///./zerosite.db')

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False  # Set to True for SQL logging
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def init_db():
    """Initialize database tables"""
    from app.models.context_snapshot import ContextSnapshot
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database initialized")

def get_db():
    """Dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
