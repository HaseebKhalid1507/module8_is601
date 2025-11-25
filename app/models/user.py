# app/models/user.py

"""
User Model

This module defines the User model for the application.
The User model represents a user in the system with authentication capabilities.
"""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    """
    User Model
    
    Represents a user in the database with authentication credentials.
    
    Attributes:
        id (int): Primary key, auto-incrementing user ID
        username (str): Unique username for the user (max 50 characters)
        email (str): Unique email address for the user (max 100 characters)
        password_hash (str): Hashed password (never store plain passwords!)
        created_at (datetime): Timestamp when the user was created (auto-generated)
        
    Constraints:
        - username must be unique
        - email must be unique
        - username, email, and password_hash cannot be null
    """
    
    # Table name in the database
    __tablename__ = "users"
    
    # Primary Key
    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="Unique identifier for each user"
    )
    
    # Username - must be unique
    username = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,  # Index for faster queries
        comment="Unique username for authentication"
    )
    
    # Email - must be unique
    email = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,  # Index for faster queries
        comment="Unique email address for the user"
    )
    
    # Password Hash - store only hashed passwords, never plain text!
    password_hash = Column(
        String(255),
        nullable=False,
        comment="Hashed password using bcrypt or similar"
    )
    
    # Timestamp - automatically set when record is created
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),  # Automatically set to current timestamp
        nullable=False,
        comment="Timestamp when the user account was created"
    )
    
    def __repr__(self):
        """
        String representation of the User object.
        Useful for debugging and logging.
        
        Returns:
            str: A readable representation of the user
        """
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
    
    def __str__(self):
        """
        User-friendly string representation.
        
        Returns:
            str: The username of the user
        """
        return self.username
    
    def to_dict(self):
        """
        Convert the User object to a dictionary.
        Useful for API responses. Does not include password_hash for security.
        
        Returns:
            dict: Dictionary representation of the user (without password)
        """
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
