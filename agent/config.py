"""
Agent Configuration
"""
import os
from dotenv import load_dotenv
import uuid

load_dotenv()


class AgentConfig:
    """Agent configuration"""

    # Device Configuration
    device_id: str = os.getenv("DEVICE_ID", str(uuid.uuid4()))
    device_name: str = os.getenv("DEVICE_NAME", "Laptop")

    # Backend Configuration
    backend_url: str = os.getenv("BACKEND_URL", "ws://localhost:8000")
    api_token: str = os.getenv("API_TOKEN", "")

    # WebSocket Configuration
    reconnect_delay: int = int(os.getenv("RECONNECT_DELAY", "5"))
    max_reconnect_attempts: int = int(os.getenv("MAX_RECONNECT_ATTEMPTS", "10"))
    message_timeout: int = int(os.getenv("MESSAGE_TIMEOUT", "60"))

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # Command Execution
    command_timeout: int = int(os.getenv("COMMAND_TIMEOUT", "30"))
    enable_system_commands: bool = os.getenv("ENABLE_SYSTEM_COMMANDS", "true").lower() == "true"

    def __init__(self):
        """Initialize and validate configuration"""
        if not self.api_token:
            raise ValueError("API_TOKEN must be set in environment variables")

    def to_dict(self):
        """Convert configuration to dictionary"""
        return {
            "device_id": self.device_id,
            "device_name": self.device_name,
            "backend_url": self.backend_url,
            "reconnect_delay": self.reconnect_delay,
            "max_reconnect_attempts": self.max_reconnect_attempts,
            "message_timeout": self.message_timeout,
            "command_timeout": self.command_timeout,
        }
