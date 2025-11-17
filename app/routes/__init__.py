# app/routes/__init__.py

"""
Routes Package

This package contains all API route modules.
"""

from app.routes.users import router as users_router

__all__ = ["users_router"]
