"""
Security utilities for authentication and token management.
"""
import os
import secrets
import json
from datetime import datetime
from functools import lru_cache


class SecurityManager:
    """Security management for API tokens and authentication."""

    def __init__(self):
        self.secret_key = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
        self.algorithm = "HS256"

    @staticmethod
    def generate_token(length: int = 32) -> str:
        """Generate a secure random token."""
        return secrets.token_urlsafe(length)

    @staticmethod
    def hash_token(token: str) -> str:
        """Hash a token (placeholder for bcrypt in production)."""
        import hashlib
        return hashlib.sha256(token.encode()).hexdigest()

    @staticmethod
    def verify_token(token: str, hashed_token: str) -> bool:
        """Verify a token against its hash."""
        import hashlib
        return hashlib.sha256(token.encode()).hexdigest() == hashed_token

    @staticmethod
    def validate_api_token(token: str) -> bool:
        """Validate API token format."""
        return len(token) >= 32


security_manager = SecurityManager()
