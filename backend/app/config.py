"""
Backend Configuration
"""
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings"""

    # API Configuration
    API_TITLE = "Laptop Control API"
    API_VERSION = "1.0.0"
    API_DESCRIPTION = "Remote Laptop Control System with Real-time Communication"

    # Database Configuration
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./laptop_control.db"
    )

    # JWT Configuration
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        "your-secret-key-change-in-production"
    )
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30

    # WebSocket Configuration
    WS_HEARTBEAT_INTERVAL = 30  # seconds
    WS_HEARTBEAT_TIMEOUT = 60   # seconds

    # Device Configuration
    DEVICE_REGISTRATION_ENABLED = True
    MAX_COMMAND_QUEUE_SIZE = 1000
    COMMAND_TIMEOUT = 30  # seconds

    # CORS Configuration
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:8100",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8100",
    ]

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")


settings = Settings()
