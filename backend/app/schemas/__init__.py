"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, Any, Dict
from app.models import CommandStatus, DeviceStatus


# ==================== User Schemas ====================
class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(UserBase):
    id: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Token Schemas ====================
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class APITokenCreate(BaseModel):
    name: str
    expires_in_days: Optional[int] = None


class APITokenResponse(BaseModel):
    id: str
    name: str
    is_active: bool
    last_used: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Device Schemas ====================
class DeviceRegister(BaseModel):
    """Device registration request"""
    device_id: str
    name: str
    device_type: str = "laptop"
    os_type: Optional[str] = None


class DeviceResponse(BaseModel):
    """Device response"""
    id: str
    device_id: str
    name: str
    device_type: str
    os_type: Optional[str]
    status: DeviceStatus
    last_seen: datetime
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class DeviceStatusUpdate(BaseModel):
    """Device status update"""
    status: DeviceStatus
    os_type: Optional[str] = None
    system_info: Optional[Dict[str, Any]] = None


# ==================== Command Schemas ====================
class CommandRequest(BaseModel):
    """Command request from mobile app"""
    device_id: str
    command_type: str
    parameters: Optional[Dict[str, Any]] = None


class CommandResponse(BaseModel):
    """Command response"""
    id: str
    device_id: str
    command_type: str
    status: CommandStatus
    result: Optional[Any]
    error_message: Optional[str]
    execution_time: Optional[int]
    sent_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class CommandStatus_(BaseModel):
    """Command status check"""
    id: str
    status: CommandStatus
    result: Optional[Any]
    error_message: Optional[str]
    execution_time: Optional[int]

    class Config:
        from_attributes = True


# ==================== WebSocket Schemas ====================
class WebSocketMessage(BaseModel):
    """Generic WebSocket message format"""
    type: str  # "command", "response", "heartbeat", "error"
    payload: Dict[str, Any]
    timestamp: datetime = datetime.utcnow()


class CommandExecutionRequest(BaseModel):
    """Command sent from backend to agent"""
    command_id: str
    command_type: str
    parameters: Optional[Dict[str, Any]] = None


class CommandExecutionResult(BaseModel):
    """Result sent from agent back to backend"""
    command_id: str
    status: CommandStatus
    result: Optional[Any]
    error_message: Optional[str]
    execution_time: int  # milliseconds


# ==================== System Monitoring Schemas ====================
class SystemMetrics(BaseModel):
    """System monitoring metrics"""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    battery_status: Optional[Dict[str, Any]]
    timestamp: datetime


class SystemInfo(BaseModel):
    """System information"""
    os: str
    platform: str
    processor: str
    cpu_count: int
    total_memory: int
    disk_space: Dict[str, int]
