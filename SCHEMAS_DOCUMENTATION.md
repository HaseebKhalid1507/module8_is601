# Pydantic Schemas Documentation

## Overview

Pydantic schemas provide data validation, serialization, and documentation for your FastAPI application. They define the structure of data for API requests and responses, ensuring type safety and automatic validation.

---

## 📋 Available Schemas

### 1. `UserCreate`

**Purpose**: Validate data when creating a new user (registration)

**Location**: `app/schemas/user.py`

**Fields**:
- `username` (str, required): 3-50 characters
- `email` (EmailStr, required): Valid email format
- `password` (str, required): Minimum 8 characters

**Example Request**:
```json
{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePass123!"
}
```

**Usage**:
```python
from app.schemas import UserCreate

@router.post("/users/")
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    # user_data is automatically validated
    # Access fields: user_data.username, user_data.email, user_data.password
    pass
```

---

### 2. `UserRead`

**Purpose**: Return user data in API responses (excludes sensitive information)

**Location**: `app/schemas/user.py`

**Fields**:
- `id` (int): Unique user identifier
- `username` (str): Username
- `email` (str): Email address
- `created_at` (datetime): Account creation timestamp

**Example Response**:
```json
{
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "created_at": "2025-11-17T10:30:00"
}
```

**Key Features**:
- ✅ Excludes `password_hash` for security
- ✅ Works with SQLAlchemy models via `from_attributes=True`
- ✅ Automatically converts datetime to ISO format

**Usage**:
```python
from app.schemas import UserRead

@router.get("/users/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    return user  # Automatically converted to UserRead schema
```

---

### 3. `UserUpdate`

**Purpose**: Validate data when updating user information

**Location**: `app/schemas/user.py`

**Fields** (all optional):
- `username` (Optional[str]): New username (3-50 characters)
- `email` (Optional[EmailStr]): New email address
- `password` (Optional[str]): New password (minimum 8 characters)

**Example Request** (partial update):
```json
{
    "email": "newemail@example.com"
}
```

**Usage**:
```python
from app.schemas.user import UserUpdate

@router.patch("/users/{user_id}")
def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    
    # Only update fields that were provided
    if user_data.username:
        user.username = user_data.username
    if user_data.email:
        user.email = user_data.email
    if user_data.password:
        user.password_hash = hash_password(user_data.password)
    
    db.commit()
    return user
```

---

### 4. `UserLogin`

**Purpose**: Validate login credentials

**Location**: `app/schemas/user.py`

**Fields**:
- `username` (str, required): Username or email
- `password` (str, required): User's password

**Example Request**:
```json
{
    "username": "john_doe",
    "password": "SecurePass123!"
}
```

**Usage**:
```python
from app.schemas.user import UserLogin

@router.post("/users/login")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(
        (User.username == credentials.username) | 
        (User.email == credentials.username)
    ).first()
    
    if user and verify_password(credentials.password, user.password_hash):
        return {"message": "Login successful"}
    
    raise HTTPException(status_code=401, detail="Invalid credentials")
```

---

## 🎯 Import Examples

### Import from schemas package:
```python
from app.schemas import UserCreate, UserRead
```

### Import specific schemas:
```python
from app.schemas.user import UserCreate, UserRead, UserUpdate, UserLogin
```

### Import all schemas:
```python
from app.schemas.user import *
```

---

## 🔍 Schema Features

### Automatic Validation

Pydantic automatically validates incoming data:

```python
# ❌ This will fail validation (email format invalid)
{
    "username": "john",
    "email": "not-an-email",
    "password": "short"
}

# Error Response:
{
    "detail": [
        {
            "loc": ["body", "email"],
            "msg": "value is not a valid email address",
            "type": "value_error.email"
        },
        {
            "loc": ["body", "password"],
            "msg": "ensure this value has at least 8 characters",
            "type": "value_error.any_str.min_length"
        }
    ]
}
```

### Type Conversion

Pydantic automatically converts compatible types:

```python
# Request with string number
{"username": "john", "email": "john@example.com", "password": "pass1234"}

# Automatically validated and typed correctly
```

### SQLAlchemy Integration

The `UserRead` schema works seamlessly with SQLAlchemy models:

```python
# SQLAlchemy User model instance
user = db.query(User).first()

# Automatically converts to UserRead schema
@router.get("/users/{id}", response_model=UserRead)
def get_user(id: int):
    return user  # Pydantic handles the conversion
```

---

## 📚 Best Practices

### 1. **Separate Input and Output Schemas**

✅ **Good**:
```python
class UserCreate(BaseModel):  # For input
    username: str
    password: str

class UserRead(BaseModel):    # For output (no password)
    id: int
    username: str
```

❌ **Bad**:
```python
class User(BaseModel):  # Same schema for input and output
    id: int
    username: str
    password: str  # Exposing password in responses!
```

### 2. **Use Field Validators**

```python
from pydantic import field_validator

class UserCreate(BaseModel):
    username: str
    password: str
    
    @field_validator('username')
    def username_alphanumeric(cls, v):
        if not v.isalnum():
            raise ValueError('Username must be alphanumeric')
        return v
```

### 3. **Provide Examples**

```python
class UserCreate(BaseModel):
    username: str = Field(..., examples=["john_doe"])
    email: EmailStr = Field(..., examples=["john@example.com"])
```

This enhances API documentation in Swagger UI.

### 4. **Use Optional for Updates**

```python
from typing import Optional

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
```

---

## 🧪 Testing Schemas

```python
from app.schemas import UserCreate, UserRead

def test_user_create_validation():
    # Valid data
    user = UserCreate(
        username="john_doe",
        email="john@example.com",
        password="SecurePass123"
    )
    assert user.username == "john_doe"
    
    # Invalid data (will raise ValidationError)
    try:
        UserCreate(
            username="ab",  # Too short
            email="invalid",
            password="short"
        )
    except ValidationError as e:
        print(e.errors())
```

---

## 📖 Additional Resources

- **Pydantic Documentation**: https://docs.pydantic.dev/
- **FastAPI Schemas Guide**: https://fastapi.tiangolo.com/tutorial/sql-databases/#create-pydantic-models
- **Email Validation**: https://docs.pydantic.dev/usage/types/#email-str

---

## ✅ Summary

| Schema | Purpose | Use Case |
|--------|---------|----------|
| `UserCreate` | Input validation | User registration |
| `UserRead` | Output serialization | API responses |
| `UserUpdate` | Partial updates | Updating user data |
| `UserLogin` | Authentication | Login endpoints |

All schemas are located in `app/schemas/user.py` and can be imported from `app/schemas`.
