# tests/integration/test_user_api.py

"""
Integration Tests for User API Endpoints

Tests the user routes with FastAPI TestClient.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.models import User
from app.utils import hash_password


# Import main app (you'll need to update this import based on your main.py structure)
# For now, we'll create a test app
from fastapi import FastAPI
from app.routes import users_router

# Create test app
app = FastAPI()
app.include_router(users_router)

# Use in-memory SQLite for testing
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture
def test_db():
    """Create a test database"""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield TestingSessionLocal()
    
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(test_db):
    """Create a test client"""
    return TestClient(app)


class TestUserAPIEndpoints:
    """Test suite for User API endpoints"""
    
    def test_create_user_success(self, client):
        """Test successful user creation"""
        response = client.post(
            "/users/",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "SecurePass123"
            }
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert "password" not in data
        assert "password_hash" not in data
        assert "id" in data
        assert "created_at" in data
    
    def test_create_user_duplicate_username(self, client):
        """Test creating user with duplicate username"""
        # Create first user
        client.post(
            "/users/",
            json={
                "username": "testuser",
                "email": "test1@example.com",
                "password": "Password123"
            }
        )
        
        # Try to create with same username
        response = client.post(
            "/users/",
            json={
                "username": "testuser",  # Duplicate
                "email": "test2@example.com",
                "password": "Password123"
            }
        )
        
        assert response.status_code == 400
        assert "Username already registered" in response.json()["detail"]
    
    def test_create_user_duplicate_email(self, client):
        """Test creating user with duplicate email"""
        # Create first user
        client.post(
            "/users/",
            json={
                "username": "user1",
                "email": "test@example.com",
                "password": "Password123"
            }
        )
        
        # Try to create with same email
        response = client.post(
            "/users/",
            json={
                "username": "user2",
                "email": "test@example.com",  # Duplicate
                "password": "Password123"
            }
        )
        
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]
    
    def test_create_user_invalid_email(self, client):
        """Test creating user with invalid email"""
        response = client.post(
            "/users/",
            json={
                "username": "testuser",
                "email": "not-an-email",
                "password": "Password123"
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_create_user_short_password(self, client):
        """Test creating user with too short password"""
        response = client.post(
            "/users/",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "short"
            }
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_get_all_users(self, client):
        """Test getting all users"""
        # Create multiple users
        for i in range(3):
            client.post(
                "/users/",
                json={
                    "username": f"user{i}",
                    "email": f"user{i}@example.com",
                    "password": "Password123"
                }
            )
        
        response = client.get("/users/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert all("password" not in user for user in data)
        assert all("password_hash" not in user for user in data)
    
    def test_get_user_by_id(self, client):
        """Test getting a specific user by ID"""
        # Create a user
        create_response = client.post(
            "/users/",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "Password123"
            }
        )
        user_id = create_response.json()["id"]
        
        # Get the user
        response = client.get(f"/users/{user_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert data["username"] == "testuser"
        assert "password" not in data
    
    def test_get_user_not_found(self, client):
        """Test getting a non-existent user"""
        response = client.get("/users/999")
        
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]
    
    def test_login_success(self, client):
        """Test successful login"""
        # Create a user
        client.post(
            "/users/",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "Password123"
            }
        )
        
        # Login
        response = client.post(
            "/users/login",
            json={
                "username": "testuser",
                "password": "Password123"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "Login successful"
    
    def test_login_with_email(self, client):
        """Test login with email instead of username"""
        # Create a user
        client.post(
            "/users/",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "Password123"
            }
        )
        
        # Login with email
        response = client.post(
            "/users/login",
            json={
                "username": "test@example.com",  # Using email
                "password": "Password123"
            }
        )
        
        assert response.status_code == 200
    
    def test_login_wrong_password(self, client):
        """Test login with wrong password"""
        # Create a user
        client.post(
            "/users/",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "CorrectPassword123"
            }
        )
        
        # Login with wrong password
        response = client.post(
            "/users/login",
            json={
                "username": "testuser",
                "password": "WrongPassword123"
            }
        )
        
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]
    
    def test_login_user_not_found(self, client):
        """Test login with non-existent user"""
        response = client.post(
            "/users/login",
            json={
                "username": "nonexistent",
                "password": "Password123"
            }
        )
        
        assert response.status_code == 401
    
    def test_delete_user(self, client):
        """Test deleting a user"""
        # Create a user
        create_response = client.post(
            "/users/",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "Password123"
            }
        )
        user_id = create_response.json()["id"]
        
        # Delete the user
        response = client.delete(f"/users/{user_id}")
        
        assert response.status_code == 204
        
        # Verify deletion
        get_response = client.get(f"/users/{user_id}")
        assert get_response.status_code == 404
    
    def test_delete_user_not_found(self, client):
        """Test deleting a non-existent user"""
        response = client.delete("/users/999")
        
        assert response.status_code == 404
