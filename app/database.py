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
logger.info(f"🔍 DATABASE_URL: {DATABASE_URL}")

# Create engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False  # Set to True for SQL logging
)
logger.info(f"✅ SQLAlchemy engine created for: {DATABASE_URL}")

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

def init_db():
    """Initialize database tables"""
    from app.models.context_snapshot import ContextSnapshot
    logger.info(f"📝 Creating tables in DB: {DATABASE_URL}")
    Base.metadata.create_all(bind=engine)
    logger.info(f"✅ Database initialized with tables: {list(Base.metadata.tables.keys())}")

def get_db():
    """Dependency for FastAPI"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
