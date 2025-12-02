# app/dependencies/auth.py

"""
Authentication Dependencies

This module provides FastAPI dependencies for JWT-based authentication.
Use these dependencies to protect routes that require authentication.
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models import User
from app.utils.jwt import verify_token, TokenData

# OAuth2 scheme - expects token in Authorization header as "Bearer <token>"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.
    
    Args:
        token: JWT token from Authorization header
        db: Database session
        
    Returns:
        User: The authenticated user object
        
    Raises:
        HTTPException: 401 if token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Verify the token
    token_data: Optional[TokenData] = verify_token(token)
    if token_data is None:
        raise credentials_exception
    
    # Get user from database
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_user_optional(
    token: Optional[str] = Depends(OAuth2PasswordBearer(tokenUrl="/users/login", auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Dependency to optionally get the current user (doesn't raise error if not authenticated).
    
    Args:
        token: Optional JWT token from Authorization header
        db: Database session
        
    Returns:
        User or None: The authenticated user object, or None if not authenticated
    """
    if token is None:
        return None
    
    token_data = verify_token(token)
    if token_data is None:
        return None
    
    user = db.query(User).filter(User.username == token_data.username).first()
    return user
