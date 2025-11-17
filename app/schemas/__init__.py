# app/schemas/__init__.py

"""
Schemas Package

This package contains all Pydantic schemas for request/response validation.
"""

from app.schemas.user import UserCreate, UserRead

__all__ = ["UserCreate", "UserRead"]
