"""Models for User, Device, and Command entities"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database import Base
import enum
import uuid


class CommandStatus(str, enum.Enum):
    """Command execution status"""
    PENDING = "pending"
    SENT = "sent"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class DeviceStatus(str, enum.Enum):
    """Device connection status"""
    OFFLINE = "offline"
    ONLINE = "online"
    IDLE = "idle"


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    devices = relationship("Device", back_populates="owner")
    api_tokens = relationship("APIToken", back_populates="user")

    def __repr__(self):
        return f"<User {self.username}>"


class APIToken(Base):
    """API Token model for device authentication"""
    __tablename__ = "api_tokens"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    token = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    last_used = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="api_tokens")

    def __repr__(self):
        return f"<APIToken {self.name}>"


class Device(Base):
    """Device/Laptop model"""
    __tablename__ = "devices"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    device_id = Column(String, unique=True, index=True, nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    device_type = Column(String, default="laptop")
    os_type = Column(String, nullable=True)  # Windows, Linux, macOS
    status = Column(SQLEnum(DeviceStatus), default=DeviceStatus.OFFLINE)
    last_seen = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owner = relationship("User", back_populates="devices")
    commands = relationship("Command", back_populates="device")

    def __repr__(self):
        return f"<Device {self.name} ({self.device_id})>"


class Command(Base):
    """Command execution model"""
    __tablename__ = "commands"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    device_id = Column(String, ForeignKey("devices.id"), nullable=False)
    command_type = Column(String, nullable=False)  # open_chrome, screenshot, etc.
    parameters = Column(Text, nullable=True)  # JSON parameters
    status = Column(SQLEnum(CommandStatus), default=CommandStatus.PENDING)
    result = Column(Text, nullable=True)  # JSON result
    error_message = Column(Text, nullable=True)
    execution_time = Column(Integer, nullable=True)  # milliseconds
    sent_at = Column(DateTime, default=datetime.utcnow)
    executed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    device = relationship("Device", back_populates="commands")

    def __repr__(self):
        return f"<Command {self.command_type} ({self.status})>"
