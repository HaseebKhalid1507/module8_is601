# app/init_db.py

"""
Database Initialization Script

This script creates all database tables defined in the SQLAlchemy models.
Run this script to set up your database schema.

Usage:
    python -m app.init_db
"""

from app.database import engine, Base
from app.models import User  # Import all models here
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_db():
    """
    Initialize the database by creating all tables.
    
    This function will:
    1. Connect to the database using the configured engine
    2. Create all tables defined in Base.metadata
    3. If tables already exist, they will not be recreated
    """
    logger.info("Creating database tables...")
    
    try:
        # Create all tables defined in the models
        Base.metadata.create_all(bind=engine)
        logger.info("✓ Database tables created successfully!")
        logger.info(f"✓ Created tables: {', '.join(Base.metadata.tables.keys())}")
    except Exception as e:
        logger.error(f"✗ Error creating database tables: {e}")
        raise


if __name__ == "__main__":
    init_db()
