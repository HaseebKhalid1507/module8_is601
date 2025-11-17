# Database Setup Guide

This guide explains how to set up and use the PostgreSQL database with your FastAPI application.

## Overview

The application now includes:
- **PostgreSQL Database**: Running in Docker via docker-compose
- **SQLAlchemy ORM**: For database interactions
- **User Model**: With username, email, password_hash, and created_at fields
- **Password Hashing**: Using bcrypt for secure password storage

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start Services with Docker Compose

```bash
docker-compose up --build
```

This will start:
- FastAPI application on port 8000
- PostgreSQL database on port 5432

### 3. Initialize the Database

In a new terminal, run:

```bash
# Option 1: From outside the container
docker exec -it fastapi_calculator python -m app.init_db

# Option 2: From inside the container
docker-compose exec web python -m app.init_db
```

This creates the `users` table in the database.

## Database Configuration

### Connection Details

The database connection is configured in `app/database.py`:

- **Host**: `postgres` (Docker service name) or `localhost` (from host machine)
- **Port**: `5432` (internal), `5433` (external/host access)
- **Database**: `calculator_db`
- **Username**: `postgres`
- **Password**: `postgres`

**Note:** Port 5433 is used on the host to avoid conflicts with other PostgreSQL instances. Inside Docker, services communicate using port 5432.

### Environment Variable

You can override the database URL using the `DATABASE_URL` environment variable:

```bash
export DATABASE_URL="postgresql://user:password@host:port/database"
```

Or in `docker-compose.yml`:

```yaml
environment:
  - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/calculator_db
```

## User Model

### Schema

The `User` model (`app/models/user.py`) has the following fields:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | Primary Key, Auto-increment | Unique user identifier |
| `username` | String(50) | Unique, Not Null, Indexed | User's username |
| `email` | String(100) | Unique, Not Null, Indexed | User's email address |
| `password_hash` | String(255) | Not Null | Bcrypt hashed password |
| `created_at` | DateTime | Auto-generated | Account creation timestamp |

### Usage Example

```python
from sqlalchemy.orm import Session
from app.models import User
from app.utils import hash_password
from app.database import SessionLocal

# Create a database session
db = SessionLocal()

# Create a new user
new_user = User(
    username="john_doe",
    email="john@example.com",
    password_hash=hash_password("secure_password123")
)

# Add to database
db.add(new_user)
db.commit()
db.refresh(new_user)

print(f"Created user: {new_user.username} with ID: {new_user.id}")

# Query users
all_users = db.query(User).all()
user_by_email = db.query(User).filter(User.email == "john@example.com").first()

# Close session
db.close()
```

## Password Hashing

### Hash a Password

```python
from app.utils import hash_password

hashed = hash_password("my_password")
# Returns: '$2b$12$...' (bcrypt hash)
```

### Verify a Password

```python
from app.utils import verify_password

is_valid = verify_password("my_password", hashed)
# Returns: True if password matches, False otherwise
```

## FastAPI Integration

### Using Database in Routes

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User

@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [user.to_dict() for user in users]

@app.post("/users")
def create_user(username: str, email: str, password: str, db: Session = Depends(get_db)):
    from app.utils import hash_password
    
    new_user = User(
        username=username,
        email=email,
        password_hash=hash_password(password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user.to_dict()
```

## Database Management

### Access PostgreSQL CLI

```bash
# Option 1: From Docker container (recommended)
docker exec -it postgres_db psql -U postgres -d calculator_db

# Option 2: From host machine (if you have psql installed)
psql -h localhost -p 5433 -U postgres -d calculator_db

# Common PostgreSQL commands:
\dt                    # List all tables
\d users              # Describe users table
SELECT * FROM users;  # Query users
\q                    # Quit
```

### Reset Database

```bash
# Stop containers and remove volumes (for calculator project only)
docker-compose down -v

# Start fresh
docker-compose up --build

# Reinitialize database
docker-compose exec web python -m app.init_db
```

**Note:** The calculator project uses a separate volume (`calculator_postgres_data`) to avoid conflicts with other PostgreSQL instances.

### View Database Logs

```bash
docker-compose logs postgres
```

## Troubleshooting

### Connection Issues

If you can't connect to the database:

1. Check if PostgreSQL is running:
   ```bash
   docker-compose ps
   ```

2. Check PostgreSQL logs:
   ```bash
   docker-compose logs postgres
   ```

3. Verify database credentials in `docker-compose.yml`

### Import Errors

If you see import errors for `sqlalchemy` or `bcrypt`:

```bash
pip install -r requirements.txt
```

Or inside Docker:

```bash
docker-compose exec web pip install -r requirements.txt
```

### Table Not Found

If you get "relation 'users' does not exist":

```bash
docker-compose exec web python -m app.init_db
```

## Security Notes

⚠️ **Important**: The default database credentials (`postgres`/`postgres`) are for development only.

For production:

1. Use strong passwords
2. Store credentials in environment variables or secrets management
3. Enable SSL/TLS for database connections
4. Restrict database network access
5. Regular security audits and updates

## Next Steps

- Add user registration endpoint
- Add user login endpoint with JWT tokens
- Add password reset functionality
- Add user profile management
- Implement role-based access control (RBAC)
