#!/usr/bin/env python3
"""
Database Migration Script for ZeroSite v11.0
=============================================

Purpose: Create/update database tables for production deployment
Date: 2025-12-27
Author: ZeroSite Team

Tables created:
1. context_snapshots - Permanent storage for pipeline contexts

Usage:
    python3 scripts/migrate_db.py
    
Environment Variables:
    DATABASE_URL - Database connection string (default: sqlite:///zerosite.db)
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker
from app.models.context_snapshot import Base, ContextSnapshot
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseMigration:
    """Handle database migrations"""
    
    def __init__(self, database_url: str = None):
        """
        Initialize migration
        
        Args:
            database_url: Database connection string
        """
        self.database_url = database_url or os.getenv(
            'DATABASE_URL',
            'sqlite:///zerosite.db'
        )
        self.engine = create_engine(self.database_url)
        self.Session = sessionmaker(bind=self.engine)
    
    def check_table_exists(self, table_name: str) -> bool:
        """Check if table exists"""
        inspector = inspect(self.engine)
        return table_name in inspector.get_table_names()
    
    def create_tables(self):
        """Create all tables"""
        logger.info("🔧 Creating database tables...")
        
        try:
            # Create all tables defined in Base
            Base.metadata.create_all(self.engine)
            logger.info("✅ Tables created successfully")
            
            # List created tables
            inspector = inspect(self.engine)
            tables = inspector.get_table_names()
            logger.info(f"📋 Available tables: {', '.join(tables)}")
            
            # Show context_snapshots schema
            if 'context_snapshots' in tables:
                columns = inspector.get_columns('context_snapshots')
                logger.info("📊 context_snapshots schema:")
                for col in columns:
                    logger.info(f"   - {col['name']}: {col['type']}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create tables: {e}")
            return False
    
    def migrate(self):
        """Run full migration"""
        logger.info("🚀 Starting database migration...")
        logger.info(f"📍 Database: {self.database_url}")
        
        # Check existing tables
        inspector = inspect(self.engine)
        existing_tables = inspector.get_table_names()
        
        if existing_tables:
            logger.info(f"📋 Existing tables: {', '.join(existing_tables)}")
        else:
            logger.info("📋 No existing tables found")
        
        # Create/update tables
        success = self.create_tables()
        
        if success:
            logger.info("✅ Migration completed successfully!")
            return 0
        else:
            logger.error("❌ Migration failed!")
            return 1
    
    def verify(self):
        """Verify migration"""
        logger.info("🔍 Verifying migration...")
        
        try:
            session = self.Session()
            
            # Test context_snapshots table
            if self.check_table_exists('context_snapshots'):
                count = session.query(ContextSnapshot).count()
                logger.info(f"✅ context_snapshots: {count} records")
            else:
                logger.error("❌ context_snapshots table not found!")
                return False
            
            session.close()
            logger.info("✅ Verification passed!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Verification failed: {e}")
            return False


def main():
    """Main entry point"""
    print("=" * 60)
    print("ZeroSite v11.0 - Database Migration")
    print("=" * 60)
    print()
    
    # Get database URL from environment or use default
    db_url = os.getenv('DATABASE_URL', 'sqlite:///zerosite.db')
    
    # Run migration
    migration = DatabaseMigration(database_url=db_url)
    exit_code = migration.migrate()
    
    if exit_code == 0:
        # Verify migration
        print()
        if migration.verify():
            print()
            print("=" * 60)
            print("✅ Migration and verification completed successfully!")
            print("=" * 60)
        else:
            print()
            print("=" * 60)
            print("⚠️  Migration completed but verification failed!")
            print("=" * 60)
            exit_code = 2
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
