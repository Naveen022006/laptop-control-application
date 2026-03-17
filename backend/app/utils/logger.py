"""
Logging configuration.
"""
import logging
import os
from logging.handlers import RotatingFileHandler

LOG_DIR = "logs"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Create logs directory
os.makedirs(LOG_DIR, exist_ok=True)


def setup_logger(name: str) -> logging.Logger:
    """Setup logger with file and console handlers."""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL))

    # File handler
    file_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, f"{name}.log"),
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(getattr(logging, LOG_LEVEL))

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, LOG_LEVEL))

    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# Root logger
root_logger = setup_logger("laptop_control")
