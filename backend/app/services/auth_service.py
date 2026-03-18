"""
Authentication service
"""
from sqlalchemy.orm import Session
from app.models import User, APIToken
from app.utils import hash_password, verify_password, create_access_token, create_api_token
from app.utils.logger import get_logger
from datetime import datetime, timedelta
from typing import Optional
import secrets

logger = get_logger(__name__)


class AuthService:
    """Authentication service"""

    @staticmethod
    def create_user(db: Session, username: str, email: str, password: str) -> User:
        """Create a new user"""
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            raise ValueError(f"User with username or email already exists")

        # Create new user
        user = User(
            username=username,
            email=email,
            hashed_password=hash_password(password)
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        logger.info(f"User created: {username}")
        return user

    @staticmethod
    def authenticate_user(
        db: Session,
        username: str,
        password: str
    ) -> Optional[User]:
        """Authenticate user with username and password"""
        user = db.query(User).filter(User.username == username).first()

        if not user or not verify_password(password, user.hashed_password):
            logger.warning(f"Failed authentication attempt for: {username}")
            return None

        logger.info(f"User authenticated: {username}")
        return user

    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def create_api_token(
        db: Session,
        user_id: str,
        token_name: str,
        expires_in_days: Optional[int] = None
    ) -> APIToken:
        """Create API token for a user"""
        token = APIToken(
            user_id=user_id,
            token=create_api_token(),
            name=token_name,
            expires_at=datetime.utcnow() + timedelta(days=expires_in_days)
            if expires_in_days else None
        )
        db.add(token)
        db.commit()
        db.refresh(token)

        logger.info(f"API token created: {token_name} for user {user_id}")
        return token

    @staticmethod
    def verify_api_token(db: Session, token: str) -> Optional[APIToken]:
        """Verify API token"""
        api_token = db.query(APIToken).filter(APIToken.token == token).first()

        if not api_token or not api_token.is_active:
            return None

        if api_token.expires_at and api_token.expires_at < datetime.utcnow():
            return None

        # Update last used timestamp
        api_token.last_used = datetime.utcnow()
        db.commit()

        return api_token

    @staticmethod
    def get_user_tokens(db: Session, user_id: str):
        """Get all tokens for a user"""
        return db.query(APIToken).filter(
            APIToken.user_id == user_id,
            APIToken.is_active == True
        ).all()

    @staticmethod
    def revoke_token(db: Session, token_id: str) -> bool:
        """Revoke an API token"""
        token = db.query(APIToken).filter(APIToken.id == token_id).first()
        if token:
            token.is_active = False
            db.commit()
            logger.info(f"Token revoked: {token_id}")
            return True
        return False
