"""
SQLAlchemy models for database tables.
"""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Integer, Text, Enum as SQLEnum
from sqlalchemy.sql import func
from enum import Enum
from .database import Base


class CommandStatus(str, Enum):
    """Command execution status."""
    PENDING = "pending"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


class Device(Base):
    """Device registration model."""
    __tablename__ = "devices"

    device_id = Column(String(255), primary_key=True, index=True)
    device_name = Column(String(255), nullable=False)
    device_type = Column(String(50), nullable=False)  # laptop, mobile
    api_token = Column(String(500), unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)
    last_online = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Command(Base):
    """Command execution logging model."""
    __tablename__ = "commands"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(255), index=True, nullable=False)
    command_name = Column(String(100), nullable=False)
    command_params = Column(Text, nullable=True)  # JSON string
    status = Column(SQLEnum(CommandStatus), default=CommandStatus.PENDING, index=True)
    result = Column(Text, nullable=True)  # JSON response
    error_message = Column(Text, nullable=True)
    execution_time = Column(Integer, nullable=True)  # milliseconds
    created_at = Column(DateTime, server_default=func.now())
    executed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class SystemMetrics(Base):
    """System metrics logging model."""
    __tablename__ = "system_metrics"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(255), index=True, nullable=False)
    cpu_percent = Column(Integer, nullable=False)
    memory_percent = Column(Integer, nullable=False)
    disk_percent = Column(Integer, nullable=False)
    temperature = Column(Integer, nullable=True)
    battery_percent = Column(Integer, nullable=True)
    is_charging = Column(Boolean, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
