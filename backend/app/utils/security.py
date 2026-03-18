"""
Security utilities - password hashing and JWT handling
"""
import hashlib
import secrets
import bcrypt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
import jwt
from app.config import settings

# Fallback pwd_context for passlib compatibility
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Hash a password using bcrypt with fallback to SHA256 for long passwords"""
    password_bytes = password.encode()

    # If password is too long for bcrypt (72 bytes), use SHA256 instead
    if len(password_bytes) > 72:
        salt = secrets.token_hex(16)
        hash_obj = hashlib.sha256((salt + password).encode())
        return f"sha256${salt}${hash_obj.hexdigest()}"

    # Use bcrypt for normal passwords
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash - supports bcrypt and SHA256"""
    try:
        # Check if it's a SHA256 hash (starts with "sha256$")
        if hashed_password.startswith("sha256$"):
            parts = hashed_password.split("$")
            if len(parts) == 3:
                salt = parts[1]
                stored_hash = parts[2]
                hash_obj = hashlib.sha256((salt + plain_password).encode())
                return hash_obj.hexdigest() == stored_hash
            return False

        # Use bcrypt directly (no passlib to avoid version conflicts)
        if hashed_password.startswith("$2"):
            # It's a bcrypt hash
            try:
                result = bcrypt.checkpw(plain_password.encode(), hashed_password.encode())
                return result
            except Exception:
                return False

        # Unknown hash format
        return False
    except Exception:
        return False


# JWT token handling
def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT access token"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode JWT access token"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except jwt.InvalidTokenError:
        return None


def create_api_token() -> str:
    """Generate a random API token"""
    return secrets.token_urlsafe(32)
