# app/database.py

"""
Database Configuration Module

This module sets up the SQLAlchemy engine, session, and base class for database models.
It handles the connection to PostgreSQL and provides utilities for database operations.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database URL Configuration
# Format: postgresql://username:password@host:port/database
# Using environment variables for security and flexibility
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@postgres:5432/calculator_db"
)

# Create SQLAlchemy Engine
# The engine is the starting point for any SQLAlchemy application
# It manages connections to the database
engine = create_engine(
    DATABASE_URL,
    echo=True,  # Set to True to see SQL queries in logs (useful for debugging)
    pool_pre_ping=True,  # Enables connection health checks before using connections
    pool_size=10,  # Maximum number of connections to keep in the pool
    max_overflow=20  # Maximum number of connections that can be created beyond pool_size
)

# Create SessionLocal class
# Sessions are used to interact with the database
# Each instance represents a "workspace" for database operations
SessionLocal = sessionmaker(
    autocommit=False,  # Transactions must be explicitly committed
    autoflush=False,  # Changes are not automatically flushed to the database
    bind=engine  # Bind the session to our engine
)

# Create Base class for declarative models
# All database models will inherit from this base class
Base = declarative_base()


# Dependency for FastAPI routes
# This function provides a database session to route handlers
def get_db():
    """
    Database session dependency for FastAPI.
    
    Yields:
        Session: A SQLAlchemy database session
        
    Usage:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
