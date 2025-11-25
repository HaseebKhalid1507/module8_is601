# tests/unit/test_user_model.py

"""
Unit Tests for User Model

Tests the User SQLAlchemy model functionality.
"""

import pytest
from datetime import datetime
from app.models.user import User
from app.utils import hash_password


class TestUserModel:
    """Test suite for the User model"""
    
    def test_user_creation(self):
        """Test creating a User instance"""
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.password_hash == "hashed_password"
    
    def test_user_repr(self):
        """Test User __repr__ method"""
        user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        
        expected = "<User(id=1, username='testuser', email='test@example.com')>"
        assert repr(user) == expected
    
    def test_user_str(self):
        """Test User __str__ method"""
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        
        assert str(user) == "testuser"
    
    def test_user_to_dict(self):
        """Test User to_dict method"""
        user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password"
        )
        user.created_at = datetime(2025, 11, 17, 10, 30, 0)
        
        user_dict = user.to_dict()
        
        assert user_dict["id"] == 1
        assert user_dict["username"] == "testuser"
        assert user_dict["email"] == "test@example.com"
        assert user_dict["created_at"] == "2025-11-17T10:30:00"
        assert "password_hash" not in user_dict  # Security check
    
    def test_user_to_dict_excludes_password(self):
        """Test that to_dict does not expose password_hash"""
        user = User(
            id=1,
            username="testuser",
            email="test@example.com",
            password_hash="super_secret_hash"
        )
        
        user_dict = user.to_dict()
        
        assert "password_hash" not in user_dict
        assert "password" not in user_dict
