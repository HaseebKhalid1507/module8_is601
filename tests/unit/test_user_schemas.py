# tests/unit/test_user_schemas.py

"""
Unit Tests for User Schemas

Tests Pydantic schemas for data validation.
"""

import pytest
from pydantic import ValidationError
from datetime import datetime
from app.schemas import UserCreate, UserRead
from app.schemas.user import UserUpdate, UserLogin


class TestUserCreateSchema:
    """Test suite for UserCreate schema"""
    
    def test_valid_user_create(self):
        """Test creating a valid UserCreate instance"""
        data = {
            "username": "john_doe",
            "email": "john@example.com",
            "password": "SecurePass123"
        }
        user = UserCreate(**data)
        
        assert user.username == "john_doe"
        assert user.email == "john@example.com"
        assert user.password == "SecurePass123"
    
    def test_username_too_short(self):
        """Test that username must be at least 3 characters"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="ab",  # Too short
                email="test@example.com",
                password="password123"
            )
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("username",) for error in errors)
    
    def test_username_too_long(self):
        """Test that username cannot exceed 50 characters"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="a" * 51,  # Too long
                email="test@example.com",
                password="password123"
            )
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("username",) for error in errors)
    
    def test_invalid_email_format(self):
        """Test that email must be valid format"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="john_doe",
                email="not-an-email",  # Invalid format
                password="password123"
            )
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("email",) for error in errors)
    
    def test_password_too_short(self):
        """Test that password must be at least 8 characters"""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                username="john_doe",
                email="john@example.com",
                password="short"  # Too short
            )
        
        errors = exc_info.value.errors()
        assert any(error["loc"] == ("password",) for error in errors)
    
    def test_missing_required_fields(self):
        """Test that all fields are required"""
        # Missing username
        with pytest.raises(ValidationError):
            UserCreate(email="test@example.com", password="password123")
        
        # Missing email
        with pytest.raises(ValidationError):
            UserCreate(username="john_doe", password="password123")
        
        # Missing password
        with pytest.raises(ValidationError):
            UserCreate(username="john_doe", email="test@example.com")


class TestUserReadSchema:
    """Test suite for UserRead schema"""
    
    def test_valid_user_read(self):
        """Test creating a valid UserRead instance"""
        data = {
            "id": 1,
            "username": "john_doe",
            "email": "john@example.com",
            "created_at": datetime(2025, 11, 17, 10, 30, 0)
        }
        user = UserRead(**data)
        
        assert user.id == 1
        assert user.username == "john_doe"
        assert user.email == "john@example.com"
        assert user.created_at == datetime(2025, 11, 17, 10, 30, 0)
    
    def test_user_read_no_password_field(self):
        """Test that UserRead schema doesn't have password field"""
        data = {
            "id": 1,
            "username": "john_doe",
            "email": "john@example.com",
            "created_at": datetime.now()
        }
        user = UserRead(**data)
        
        # Should not have password or password_hash attributes
        assert not hasattr(user, 'password')
        assert not hasattr(user, 'password_hash')
    
    def test_user_read_missing_required_fields(self):
        """Test that all fields are required in UserRead"""
        with pytest.raises(ValidationError):
            UserRead(
                username="john_doe",
                email="john@example.com",
                created_at=datetime.now()
                # Missing id
            )


class TestUserUpdateSchema:
    """Test suite for UserUpdate schema"""
    
    def test_all_fields_optional(self):
        """Test that all fields in UserUpdate are optional"""
        # Empty update should be valid
        user_update = UserUpdate()
        assert user_update.username is None
        assert user_update.email is None
        assert user_update.password is None
    
    def test_partial_update_username(self):
        """Test updating only username"""
        user_update = UserUpdate(username="new_username")
        assert user_update.username == "new_username"
        assert user_update.email is None
        assert user_update.password is None
    
    def test_partial_update_email(self):
        """Test updating only email"""
        user_update = UserUpdate(email="new@example.com")
        assert user_update.username is None
        assert user_update.email == "new@example.com"
        assert user_update.password is None
    
    def test_update_validates_constraints(self):
        """Test that UserUpdate still validates constraints when provided"""
        # Too short username
        with pytest.raises(ValidationError):
            UserUpdate(username="ab")
        
        # Invalid email format
        with pytest.raises(ValidationError):
            UserUpdate(email="not-an-email")
        
        # Too short password
        with pytest.raises(ValidationError):
            UserUpdate(password="short")


class TestUserLoginSchema:
    """Test suite for UserLogin schema"""
    
    def test_valid_login(self):
        """Test creating a valid UserLogin instance"""
        login = UserLogin(username="john_doe", password="password123")
        
        assert login.username == "john_doe"
        assert login.password == "password123"
    
    def test_login_with_email(self):
        """Test login with email instead of username"""
        login = UserLogin(username="john@example.com", password="password123")
        
        assert login.username == "john@example.com"
        assert login.password == "password123"
    
    def test_missing_credentials(self):
        """Test that both fields are required"""
        with pytest.raises(ValidationError):
            UserLogin(username="john_doe")  # Missing password
        
        with pytest.raises(ValidationError):
            UserLogin(password="password123")  # Missing username
