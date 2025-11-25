# app/schemas/user.py

"""
User Schemas

This module defines Pydantic schemas for user data validation.
Pydantic schemas ensure data validation for API requests and responses.
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    """
    Schema for creating a new user.
    
    This schema is used for user registration and validates incoming data
    before creating a user in the database.
    
    Attributes:
        username (str): Unique username (3-50 characters)
        email (EmailStr): Valid email address
        password (str): Password (minimum 8 characters)
        
    Example:
        ```json
        {
            "username": "john_doe",
            "email": "john@example.com",
            "password": "SecurePass123!"
        }
        ```
    """
    
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Username for the account",
        examples=["john_doe", "alice_smith"]
    )
    
    email: EmailStr = Field(
        ...,
        description="Valid email address",
        examples=["user@example.com"]
    )
    
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Password for the account (minimum 8 characters)",
        examples=["SecurePassword123!"]
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "password": "MySecurePass123!"
            }
        }
    )


class UserRead(BaseModel):
    """
    Schema for reading user data.
    
    This schema is used for API responses and excludes sensitive information
    like password_hash. It represents the public view of a user.
    
    Attributes:
        id (int): Unique user identifier
        username (str): Username
        email (str): Email address
        created_at (datetime): When the account was created
        
    Example:
        ```json
        {
            "id": 1,
            "username": "john_doe",
            "email": "john@example.com",
            "created_at": "2025-11-17T10:30:00"
        }
        ```
    """
    
    id: int = Field(
        ...,
        description="Unique user identifier",
        examples=[1, 42]
    )
    
    username: str = Field(
        ...,
        description="Username",
        examples=["john_doe"]
    )
    
    email: str = Field(
        ...,
        description="Email address",
        examples=["john@example.com"]
    )
    
    created_at: datetime = Field(
        ...,
        description="Account creation timestamp",
        examples=["2025-11-17T10:30:00"]
    )
    
    model_config = ConfigDict(
        from_attributes=True,  # Allows Pydantic to work with SQLAlchemy models
        json_schema_extra={
            "example": {
                "id": 1,
                "username": "john_doe",
                "email": "john@example.com",
                "created_at": "2025-11-17T10:30:00"
            }
        }
    )


class UserUpdate(BaseModel):
    """
    Schema for updating user data.
    
    All fields are optional, allowing partial updates.
    
    Attributes:
        username (Optional[str]): New username (3-50 characters)
        email (Optional[EmailStr]): New email address
        password (Optional[str]): New password (minimum 8 characters)
    """
    
    username: Optional[str] = Field(
        None,
        min_length=3,
        max_length=50,
        description="New username (optional)"
    )
    
    email: Optional[EmailStr] = Field(
        None,
        description="New email address (optional)"
    )
    
    password: Optional[str] = Field(
        None,
        min_length=8,
        max_length=100,
        description="New password (optional, minimum 8 characters)"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "newemail@example.com"
            }
        }
    )


class UserLogin(BaseModel):
    """
    Schema for user login.
    
    Used to authenticate a user with username/email and password.
    
    Attributes:
        username (str): Username or email address
        password (str): User's password
    """
    
    username: str = Field(
        ...,
        description="Username or email address",
        examples=["john_doe", "john@example.com"]
    )
    
    password: str = Field(
        ...,
        description="User's password",
        examples=["MySecurePass123!"]
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "john_doe",
                "password": "MySecurePass123!"
            }
        }
    )
