"""
Device management routes.
"""
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from datetime import datetime

from ..models.database import get_db
from ..models.models import Device
from ..schemas.schemas import DeviceRegister, DeviceResponse, ErrorResponse
from ..utils.security import security_manager
from ..utils.logger import root_logger

router = APIRouter(prefix="/devices", tags=["devices"])
logger = root_logger


@router.post("/register", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
def register_device(
    device_data: DeviceRegister,
    db: Session = Depends(get_db)
):
    """
    Register a new device (laptop or mobile app).
    
    Returns API token for authentication in subsequent requests.
    """
    # Check if device already registered
    existing = db.query(Device).filter(Device.device_id == device_data.device_id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Device already registered"
        )

    # Generate API token
    api_token = security_manager.generate_token()

    # Create device record
    device = Device(
        device_id=device_data.device_id,
        device_name=device_data.device_name,
        device_type=device_data.device_type,
        api_token=api_token,
        is_active=True,
        last_online=datetime.utcnow()
    )

    db.add(device)
    db.commit()
    db.refresh(device)

    logger.info(f"Device registered: {device.device_id} ({device.device_type})")
    return device


@router.get("/{device_id}", response_model=DeviceResponse)
def get_device(
    device_id: str,
    db: Session = Depends(get_db)
):
    """Get device information."""
    device = db.query(Device).filter(Device.device_id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    return device


@router.put("/{device_id}/activate")
def activate_device(
    device_id: str,
    db: Session = Depends(get_db)
):
    """Activate a device."""
    device = db.query(Device).filter(Device.device_id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )

    device.is_active = True
    db.commit()
    logger.info(f"Device activated: {device_id}")
    return {"message": "Device activated", "device_id": device_id}


@router.put("/{device_id}/deactivate")
def deactivate_device(
    device_id: str,
    db: Session = Depends(get_db)
):
    """Deactivate a device."""
    device = db.query(Device).filter(Device.device_id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )

    device.is_active = False
    db.commit()
    logger.info(f"Device deactivated: {device_id}")
    return {"message": "Device deactivated", "device_id": device_id}


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_device(
    device_id: str,
    db: Session = Depends(get_db)
):
    """Delete a device."""
    device = db.query(Device).filter(Device.device_id == device_id).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )

    db.delete(device)
    db.commit()
    logger.info(f"Device deleted: {device_id}")
