"""
JWT Authentication Dependencies
"""
from fastapi import Depends, HTTPException, status
from starlette.requests import Request
from app.utils.security import decode_access_token
from app.utils.logger import get_logger
from typing import Optional

logger = get_logger(__name__)


def get_current_user_id(request: Request) -> str:
    """Extract and validate user ID from JWT token"""
    logger.info("=== AUTH DEPENDENCY CALLED ===")

    auth_header = request.headers.get("Authorization")
    logger.info(f"Auth header: {auth_header[:30] if auth_header else 'MISSING'}...")

    if not auth_header:
        logger.error("Missing authorization header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )

    # Extract token from "Bearer <token>"
    try:
        scheme, token = auth_header.split()
        logger.info(f"Scheme: {scheme}")
        if scheme.lower() != "bearer":
            logger.error(f"Invalid scheme: {scheme}")
            raise ValueError()
    except ValueError as e:
        logger.error(f"Failed to parse auth header: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )

    payload = decode_access_token(token)
    logger.info(f"Token payload: {payload}")

    if payload is None:
        logger.error("Invalid or expired token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    user_id = payload.get("sub")
    logger.info(f"Extracted user_id: {user_id}")

    if not user_id:
        logger.error("Token missing user ID")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user ID"
        )

    logger.info(f"AUTH SUCCESS: user_id={user_id}")
    return user_id



