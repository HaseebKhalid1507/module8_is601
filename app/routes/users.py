# app/routes/users.py

"""
User Routes

This module defines API endpoints for user management.
These are example routes to demonstrate how to use the User model.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserRead
from app.schemas.user import UserLogin, UserUpdate
from app.utils import hash_password, verify_password, create_access_token, TokenWithUser

# Create a router for user-related endpoints
router = APIRouter(
    prefix="/users",
    tags=["users"]
)


# Routes
@router.post("/register", response_model=TokenWithUser, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=TokenWithUser, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user and return JWT token.
    
    Args:
        user_data: User registration data (username, email, password)
        db: Database session dependency
        
    Returns:
        TokenWithUser: JWT token with user info
        
    Raises:
        HTTPException: If username or email already exists
    """
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hash_password(user_data.password)
    )
    
    # Add to database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Generate JWT token
    access_token = create_access_token(
        data={"sub": new_user.username, "user_id": new_user.id}
    )
    
    return TokenWithUser(
        access_token=access_token,
        token_type="bearer",
        user_id=new_user.id,
        username=new_user.username,
        email=new_user.email
    )


@router.get("/", response_model=List[UserRead])
def get_all_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all users (paginated).
    
    Args:
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        db: Database session dependency
        
    Returns:
        List[UserRead]: List of users (without passwords)
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return [user.to_dict() for user in users]


@router.get("/{user_id}", response_model=UserRead)
def get_user_by_id(user_id: int, db: Session = Depends(get_db)):
    """
    Get a specific user by ID.
    
    Args:
        user_id: The user's ID
        db: Database session dependency
        
    Returns:
        UserRead: The user details (without password)
        
    Raises:
        HTTPException: If user not found
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user.to_dict()


@router.post("/login", response_model=TokenWithUser)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticate a user and return JWT token.
    
    Args:
        credentials: Login credentials (username/email and password)
        db: Database session dependency
        
    Returns:
        TokenWithUser: JWT token with user info
        
    Raises:
        HTTPException: If credentials are invalid (401 Unauthorized)
    """
    # Find user by username or email
    user = db.query(User).filter(
        (User.username == credentials.username) | (User.email == credentials.username)
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Generate JWT token
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id}
    )
    
    return TokenWithUser(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        username=user.username,
        email=user.email
    )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    Delete a user.
    
    Args:
        user_id: The user's ID
        db: Database session dependency
        
    Raises:
        HTTPException: If user not found
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    db.delete(user)
    db.commit()
    
    return None
