import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")

# Create engine with future flag for SQLAlchemy 1.4+/2.0 style
engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()

def create_tables():
    """Create tables for the application (convenience helper for tests)."""
    Base.metadata.create_all(bind=engine)
