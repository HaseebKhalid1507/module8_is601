# tests/integration/test_user_database.py

"""
Integration Tests for User Database Operations

Tests User model interactions with the database.
"""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import User
from app.utils import hash_password


# Use in-memory SQLite for testing
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture
def db_engine():
    """Create a test database engine"""
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(db_engine):
    """Create a test database session"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = TestingSessionLocal()
    yield session
    session.close()


class TestUserDatabaseOperations:
    """Test suite for User database operations"""
    
    def test_create_user(self, db_session):
        """Test creating a user in the database"""
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=hash_password("password123")
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        assert user.id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.created_at is not None
    
    def test_query_user_by_username(self, db_session):
        """Test querying a user by username"""
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=hash_password("password123")
        )
        db_session.add(user)
        db_session.commit()
        
        # Query by username
        found_user = db_session.query(User).filter(User.username == "testuser").first()
        
        assert found_user is not None
        assert found_user.username == "testuser"
        assert found_user.email == "test@example.com"
    
    def test_query_user_by_email(self, db_session):
        """Test querying a user by email"""
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=hash_password("password123")
        )
        db_session.add(user)
        db_session.commit()
        
        # Query by email
        found_user = db_session.query(User).filter(User.email == "test@example.com").first()
        
        assert found_user is not None
        assert found_user.username == "testuser"
    
    def test_update_user(self, db_session):
        """Test updating a user in the database"""
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=hash_password("password123")
        )
        db_session.add(user)
        db_session.commit()
        
        # Update user
        user.email = "newemail@example.com"
        db_session.commit()
        db_session.refresh(user)
        
        assert user.email == "newemail@example.com"
    
    def test_delete_user(self, db_session):
        """Test deleting a user from the database"""
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=hash_password("password123")
        )
        db_session.add(user)
        db_session.commit()
        user_id = user.id
        
        # Delete user
        db_session.delete(user)
        db_session.commit()
        
        # Verify deletion
        found_user = db_session.query(User).filter(User.id == user_id).first()
        assert found_user is None
    
    def test_query_all_users(self, db_session):
        """Test querying all users"""
        # Create multiple users
        users = [
            User(username="user1", email="user1@example.com", password_hash=hash_password("pass1")),
            User(username="user2", email="user2@example.com", password_hash=hash_password("pass2")),
            User(username="user3", email="user3@example.com", password_hash=hash_password("pass3")),
        ]
        
        for user in users:
            db_session.add(user)
        db_session.commit()
        
        # Query all users
        all_users = db_session.query(User).all()
        
        assert len(all_users) == 3
        assert all(user.id is not None for user in all_users)
    
    def test_user_created_at_auto_set(self, db_session):
        """Test that created_at is automatically set"""
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=hash_password("password123")
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        assert user.created_at is not None
    
    def test_password_hash_stored_correctly(self, db_session):
        """Test that password hash is stored and can be verified"""
        password = "secure_password_123"
        hashed = hash_password(password)
        
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=hashed
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Verify the stored hash
        from app.utils import verify_password
        assert verify_password(password, user.password_hash)
