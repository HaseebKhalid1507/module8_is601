# Testing Documentation

## Overview

Comprehensive test suite for the User model, authentication utilities, Pydantic schemas, and API endpoints.

---

## 📁 Test Structure

```
tests/
├── unit/
│   ├── test_user_model.py       # User model tests
│   ├── test_auth_utils.py       # Password hashing tests
│   └── test_user_schemas.py     # Pydantic schema validation tests
└── integration/
    ├── test_user_database.py    # Database operation tests
    └── test_user_api.py          # API endpoint tests
```

---

## 🚀 Running Tests

### Run All Tests

```bash
pytest
```

### Run Specific Test File

```bash
# Unit tests
pytest tests/unit/test_user_model.py
pytest tests/unit/test_auth_utils.py
pytest tests/unit/test_user_schemas.py

# Integration tests
pytest tests/integration/test_user_database.py
pytest tests/integration/test_user_api.py
```

### Run Tests by Category

```bash
# Unit tests only
pytest tests/unit/

# Integration tests only
pytest tests/integration/
```

### Run with Coverage

```bash
pytest --cov=app --cov-report=html
```

Then open `htmlcov/index.html` in your browser to view coverage report.

### Run Specific Test

```bash
pytest tests/unit/test_auth_utils.py::TestPasswordHashing::test_hash_password_returns_string
```

### Verbose Output

```bash
pytest -v
```

### Stop on First Failure

```bash
pytest -x
```

---

## 📊 Test Coverage

### Unit Tests

#### **test_user_model.py** (6 tests)
- ✅ User instance creation
- ✅ String representation (`__repr__` and `__str__`)
- ✅ Dictionary conversion (`to_dict`)
- ✅ Password exclusion from output

#### **test_auth_utils.py** (11 tests)
- ✅ Password hashing returns string
- ✅ Different salts produce different hashes
- ✅ Bcrypt format validation
- ✅ Correct password verification
- ✅ Incorrect password rejection
- ✅ Case sensitivity
- ✅ Special character support
- ✅ Unicode character support
- ✅ Empty password handling
- ✅ Long password handling

#### **test_user_schemas.py** (17 tests)
- ✅ Valid schema creation
- ✅ Username length validation (min/max)
- ✅ Email format validation
- ✅ Password length validation
- ✅ Required field validation
- ✅ Optional field validation (UserUpdate)
- ✅ Partial updates
- ✅ Login schema validation
- ✅ Password field exclusion in UserRead

### Integration Tests

#### **test_user_database.py** (10 tests)
- ✅ Create user in database
- ✅ Query user by username
- ✅ Query user by email
- ✅ Update user
- ✅ Delete user
- ✅ Query all users
- ✅ Auto-generated `created_at`
- ✅ Password hash storage and verification

#### **test_user_api.py** (16 tests)
- ✅ Create user (success)
- ✅ Duplicate username handling
- ✅ Duplicate email handling
- ✅ Invalid email rejection
- ✅ Short password rejection
- ✅ Get all users
- ✅ Get user by ID
- ✅ User not found handling
- ✅ Login with username (success)
- ✅ Login with email (success)
- ✅ Wrong password handling
- ✅ Non-existent user login
- ✅ Delete user
- ✅ Delete non-existent user
- ✅ Password exclusion from responses

**Total: 60 tests**

---

## 🧪 Test Examples

### Unit Test Example

```python
def test_hash_password_returns_string():
    """Test that hash_password returns a string"""
    password = "test_password_123"
    hashed = hash_password(password)
    
    assert isinstance(hashed, str)
    assert len(hashed) > 0
```

### Integration Test Example

```python
def test_create_user_success(client):
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
    assert "password" not in data  # Security check
```

---

## 🔧 Test Configuration

### pytest.ini

Current configuration (update if needed):

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --strict-markers
    --tb=short
```

---

## 📈 Continuous Integration

### GitHub Actions Example

Create `.github/workflows/tests.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run tests
      run: pytest --cov=app --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

---

## 🐛 Debugging Failed Tests

### View Detailed Error Output

```bash
pytest -vv
```

### Print Statements in Tests

```python
def test_something():
    result = some_function()
    print(f"Result: {result}")  # Will show with pytest -s
    assert result == expected
```

Run with:
```bash
pytest -s  # Show print statements
```

### Drop into Debugger on Failure

```bash
pytest --pdb
```

### Re-run Only Failed Tests

```bash
pytest --lf  # Last failed
pytest --ff  # Failed first, then others
```

---

## 📝 Writing New Tests

### Test Naming Convention

- File: `test_<module_name>.py`
- Class: `Test<FeatureName>`
- Method: `test_<what_it_tests>`

### Good Test Structure

```python
def test_feature_name():
    """Clear description of what is being tested"""
    # Arrange - Set up test data
    user_data = {"username": "test", "email": "test@example.com"}
    
    # Act - Perform the action
    result = create_user(user_data)
    
    # Assert - Verify the result
    assert result.username == "test"
```

### Test Fixtures

```python
@pytest.fixture
def sample_user():
    """Reusable test user"""
    return User(
        username="testuser",
        email="test@example.com",
        password_hash=hash_password("password123")
    )

def test_with_fixture(sample_user):
    assert sample_user.username == "testuser"
```

---

## 🎯 Best Practices

1. **Test one thing at a time** - Each test should verify a single behavior
2. **Use descriptive names** - Test name should explain what it tests
3. **Arrange-Act-Assert** - Follow the AAA pattern
4. **Independent tests** - Tests should not depend on each other
5. **Clean up** - Use fixtures to ensure clean state
6. **Test edge cases** - Empty strings, very long inputs, special characters
7. **Test error conditions** - Not just the happy path
8. **Mock external dependencies** - Use mocks for APIs, databases in unit tests

---

## 📚 Additional Resources

- **pytest Documentation**: https://docs.pytest.org/
- **FastAPI Testing**: https://fastapi.tiangolo.com/tutorial/testing/
- **SQLAlchemy Testing**: https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites

---

## ✅ Summary

- **60 total tests** covering models, schemas, utilities, and API endpoints
- **Unit tests** for individual components
- **Integration tests** for database and API interactions
- **Comprehensive coverage** of success and error cases
- **Security validation** ensuring passwords are never exposed

Run `pytest` to execute all tests! 🎉
