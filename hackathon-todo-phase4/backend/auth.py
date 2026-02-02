"""
Better Auth with JWT Authentication Module
Provides stateless JWT-based authentication for the Todo API
"""

from datetime import datetime, timedelta
from typing import Optional
import os
import uuid
import hashlib
import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
import jwt

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", secrets.token_hex(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

security = HTTPBearer()


# Models
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenPayload(BaseModel):
    sub: str  # user_id
    email: str
    exp: datetime
    type: str  # "access" or "refresh"


# Password hashing
def hash_password(password: str) -> str:
    """Hash password using SHA-256 with salt"""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}${pwd_hash}"


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against stored hash"""
    try:
        salt, pwd_hash = hashed.split("$")
        return hashlib.sha256((password + salt).encode()).hexdigest() == pwd_hash
    except ValueError:
        return False


# Token management
def create_access_token(user_id: str, email: str) -> str:
    """Create JWT access token"""
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": user_id,
        "email": email,
        "exp": expire,
        "type": "access",
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(user_id: str, email: str) -> str:
    """Create JWT refresh token"""
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": user_id,
        "email": email,
        "exp": expire,
        "type": "refresh",
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    """Decode and validate JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


# Database operations for users
def init_users_table(conn):
    """Create users table if it doesn't exist"""
    cursor = conn.cursor()

    # Check if users table exists and get its schema
    cursor.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'id'
    """)
    existing_column = cursor.fetchone()

    if existing_column:
        # Users table exists - check if it has hashed_password column
        cursor.execute("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'users' AND column_name = 'hashed_password'
        """)
        if not cursor.fetchone():
            # Add hashed_password column if missing
            cursor.execute("""
                ALTER TABLE users ADD COLUMN IF NOT EXISTS hashed_password VARCHAR(255)
            """)
            cursor.execute("""
                ALTER TABLE users ADD COLUMN IF NOT EXISTS name VARCHAR(255)
            """)
            cursor.execute("""
                ALTER TABLE users ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            """)
    else:
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id VARCHAR(36) PRIMARY KEY,
                email VARCHAR(255) UNIQUE NOT NULL,
                hashed_password VARCHAR(255) NOT NULL,
                name VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

    conn.commit()
    cursor.close()


def create_user(conn, email: str, password: str, name: Optional[str] = None) -> dict:
    """Create a new user"""
    from psycopg2.extras import RealDictCursor

    cursor = conn.cursor(cursor_factory=RealDictCursor)

    # Check if user exists
    cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
    if cursor.fetchone():
        cursor.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    user_id = str(uuid.uuid4())
    hashed_password = hash_password(password)
    now = datetime.utcnow()

    cursor.execute(
        """
        INSERT INTO users (id, email, hashed_password, name, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        RETURNING id, email, name, created_at
        """,
        (user_id, email, hashed_password, name, now, now)
    )
    user = cursor.fetchone()
    conn.commit()
    cursor.close()

    return dict(user)


def authenticate_user(conn, email: str, password: str) -> Optional[dict]:
    """Authenticate user by email and password"""
    from psycopg2.extras import RealDictCursor

    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        "SELECT id, email, hashed_password, name, created_at FROM users WHERE email = %s",
        (email,)
    )
    user = cursor.fetchone()
    cursor.close()

    if not user:
        return None

    if not verify_password(password, user["hashed_password"]):
        return None

    return {
        "id": user["id"],
        "email": user["email"],
        "name": user["name"],
        "created_at": user["created_at"]
    }


def get_user_by_id(conn, user_id: str) -> Optional[dict]:
    """Get user by ID"""
    from psycopg2.extras import RealDictCursor

    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        "SELECT id, email, name, created_at FROM users WHERE id = %s",
        (user_id,)
    )
    user = cursor.fetchone()
    cursor.close()

    return dict(user) if user else None


# Dependency for protected routes
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Extract and validate current user from JWT token"""
    token = credentials.credentials
    payload = decode_token(token)

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )

    return {
        "user_id": payload["sub"],
        "email": payload["email"]
    }


# Optional auth - returns None if no token provided
async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    )
) -> Optional[dict]:
    """Get current user if token provided, otherwise return None"""
    if not credentials:
        return None

    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None
