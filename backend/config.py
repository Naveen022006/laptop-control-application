"""
Environment configuration management.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Base configuration."""
    DEBUG = False
    TESTING = False
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./laptop_control.db")
    
    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM = "HS256"
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    # CORS
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # API
    API_TITLE = "Laptop Control API"
    API_DESCRIPTION = "Remote Laptop Control System Backend"
    API_VERSION = "1.0.0"


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./laptop_control_dev.db")


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    DATABASE_URL = os.getenv("DATABASE_URL")  # Must be set
    SECRET_KEY = os.getenv("SECRET_KEY")  # Must be set
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "https://yourdomain.com").split(",")


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DATABASE_URL = "sqlite:///:memory:"
    SECRET_KEY = "test-secret-key"


# Get current environment
ENV = os.getenv("ENV", "development").lower()

if ENV == "production":
    config = ProductionConfig()
elif ENV == "testing":
    config = TestingConfig()
else:
    config = DevelopmentConfig()
