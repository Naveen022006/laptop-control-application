"""
Authentication routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import UserCreate, UserLogin, UserResponse, TokenResponse, APITokenCreate, APITokenResponse
from app.services import AuthService
from app.utils import create_access_token
from app.utils.auth import get_current_user_id
from app.utils.logger import get_logger
from datetime import timedelta
from app.config import settings

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get("/test")
def test_endpoint():
    """Simple test endpoint"""
    logger.info("Test endpoint called")
    return {"message": "Router working"}


@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    try:
        user = AuthService.create_user(
            db,
            username=user_data.username,
            email=user_data.email,
            password=user_data.password
        )
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login and get access token"""
    logger.info(f"Login attempt for user: {credentials.username}")
    try:
        user = AuthService.authenticate_user(
            db,
            username=credentials.username,
            password=credentials.password
        )
        logger.info(f"Auth result: {user}")

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        logger.info(f"Creating token for user ID: {user.id}")
        access_token = create_access_token(
            data={"sub": user.id, "username": user.username},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        logger.info(f"Token created successfully")

        response = {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        logger.info(f"Returning login response")
        return response
    except HTTPException:
        logger.error("HTTPException raised in login")
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/token/create", response_model=APITokenResponse)
def create_api_token(
    token_data: APITokenCreate,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """Create API token for device authentication"""
    try:
        token = AuthService.create_api_token(
            db,
            user_id=current_user_id,
            token_name=token_data.name,
            expires_in_days=token_data.expires_in_days
        )
        return token
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/tokens", response_model=list[APITokenResponse])
def get_tokens(
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """Get all API tokens for current user"""
    tokens = AuthService.get_user_tokens(db, current_user_id)
    return tokens


@router.delete("/token/{token_id}")
def revoke_token(
    token_id: str,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """Revoke an API token"""
    if AuthService.revoke_token(db, token_id):
        return {"message": "Token revoked successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found"
        )
