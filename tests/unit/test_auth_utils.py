# tests/unit/test_auth_utils.py

"""
Unit Tests for Authentication Utilities

Tests password hashing and verification functions.
"""

import pytest
from app.utils import hash_password, verify_password


class TestPasswordHashing:
    """Test suite for password hashing utilities"""
    
    def test_hash_password_returns_string(self):
        """Test that hash_password returns a string"""
        password = "test_password_123"
        hashed = hash_password(password)
        
        assert isinstance(hashed, str)
        assert len(hashed) > 0
    
    def test_hash_password_different_each_time(self):
        """Test that hashing the same password twice produces different hashes (due to salt)"""
        password = "test_password_123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        assert hash1 != hash2  # Different due to different salts
    
    def test_hash_password_bcrypt_format(self):
        """Test that hashed password follows bcrypt format"""
        password = "test_password_123"
        hashed = hash_password(password)
        
        # Bcrypt hashes start with $2b$ (or $2a$/$2y$)
        assert hashed.startswith('$2b$') or hashed.startswith('$2a$') or hashed.startswith('$2y$')
    
    def test_verify_password_correct(self):
        """Test that verify_password returns True for correct password"""
        password = "correct_password_123"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_verify_password_incorrect(self):
        """Test that verify_password returns False for incorrect password"""
        password = "correct_password_123"
        wrong_password = "wrong_password_456"
        hashed = hash_password(password)
        
        assert verify_password(wrong_password, hashed) is False
    
    def test_verify_password_case_sensitive(self):
        """Test that password verification is case-sensitive"""
        password = "CaseSensitive123"
        hashed = hash_password(password)
        
        assert verify_password("CaseSensitive123", hashed) is True
        assert verify_password("casesensitive123", hashed) is False
        assert verify_password("CASESENSITIVE123", hashed) is False
    
    def test_hash_password_with_special_characters(self):
        """Test hashing passwords with special characters"""
        password = "P@ssw0rd!#$%^&*()"
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_hash_password_with_unicode(self):
        """Test hashing passwords with unicode characters"""
        password = "пароль123"  # Russian characters
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
    
    def test_hash_password_empty_string(self):
        """Test hashing an empty password"""
        password = ""
        hashed = hash_password(password)
        
        assert isinstance(hashed, str)
        assert verify_password(password, hashed) is True
    
    def test_hash_password_long_password(self):
        """Test hashing a very long password"""
        password = "a" * 1000  # 1000 character password
        hashed = hash_password(password)
        
        assert verify_password(password, hashed) is True
