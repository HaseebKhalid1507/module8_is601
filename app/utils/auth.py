# app/utils/auth.py

"""
Authentication Utilities

This module provides utility functions for password hashing and verification
using bcrypt, a secure password hashing algorithm.
"""

import bcrypt


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Bcrypt automatically handles salt generation and provides a secure
    one-way hash that is resistant to rainbow table attacks.
    
    Args:
        password (str): The plain text password to hash
        
    Returns:
        str: The hashed password (safe to store in database)
        
    Example:
        >>> hashed = hash_password("my_secure_password")
        >>> print(hashed)
        '$2b$12$...'  # A bcrypt hash
    """
    # Convert password to bytes
    password_bytes = password.encode('utf-8')
    
    # Generate salt and hash the password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    # Return the hash as a string
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hashed password.
    
    This function checks if a plain text password matches the stored hash.
    It's used during login to verify user credentials.
    
    Args:
        plain_password (str): The plain text password to verify
        hashed_password (str): The hashed password from the database
        
    Returns:
        bool: True if the password matches, False otherwise
        
    Example:
        >>> hashed = hash_password("my_password")
        >>> verify_password("my_password", hashed)
        True
        >>> verify_password("wrong_password", hashed)
        False
    """
    # Convert both to bytes
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    
    # Check if the password matches the hash
    return bcrypt.checkpw(password_bytes, hashed_bytes)
