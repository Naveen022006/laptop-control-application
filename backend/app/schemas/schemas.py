"""
Pydantic schemas for request/response validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class DeviceRegister(BaseModel):
    """Device registration request schema."""
    device_id: str = Field(..., min_length=1, max_length=255)
    device_name: str = Field(..., min_length=1, max_length=255)
    device_type: str = Field(..., regex="^(laptop|mobile)$")


class DeviceResponse(BaseModel):
    """Device response schema."""
    device_id: str
    device_name: str
    device_type: str
    api_token: str
    is_active: bool
    last_online: datetime

    class Config:
        from_attributes = True


class CommandRequest(BaseModel):
    """Command execution request schema."""
    command_name: str = Field(..., min_length=1, max_length=100)
    command_params: Optional[Dict[str, Any]] = Field(default=None)


class CommandResponse(BaseModel):
    """Command response schema."""
    id: int
    device_id: str
    command_name: str
    status: str
    result: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    executed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SystemMetricsRequest(BaseModel):
    """System metrics request schema."""
    cpu_percent: int = Field(..., ge=0, le=100)
    memory_percent: int = Field(..., ge=0, le=100)
    disk_percent: int = Field(..., ge=0, le=100)
    temperature: Optional[int] = None
    battery_percent: Optional[int] = Field(None, ge=0, le=100)
    is_charging: Optional[bool] = None


class SystemMetricsResponse(BaseModel):
    """System metrics response schema."""
    id: int
    device_id: str
    cpu_percent: int
    memory_percent: int
    disk_percent: int
    temperature: Optional[int]
    battery_percent: Optional[int]
    is_charging: Optional[bool]
    created_at: datetime

    class Config:
        from_attributes = True


class AuthToken(BaseModel):
    """Authentication token response."""
    access_token: str
    token_type: str = "bearer"
    device_id: str


class ErrorResponse(BaseModel):
    """Error response schema."""
    detail: str
    error_code: Optional[str] = None
