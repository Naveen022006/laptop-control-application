"""
Device management routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import DeviceRegister, DeviceResponse, DeviceStatusUpdate
from app.services import DeviceService
from app.models import DeviceStatus
from app.utils.auth import get_current_user_id
from typing import List

router = APIRouter(prefix="/devices", tags=["Devices"])


@router.post("/register", response_model=DeviceResponse)
def register_device(
    device_data: DeviceRegister,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """Register a new device"""
    try:
        device = DeviceService.register_device(
            db,
            user_id=current_user_id,
            device_id=device_data.device_id,
            name=device_data.name,
            device_type=device_data.device_type,
            os_type=device_data.os_type
        )
        return device
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=List[DeviceResponse])
def list_devices(
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """Get all devices for current user"""
    devices = DeviceService.get_user_devices(db, current_user_id)
    return devices


@router.get("/{device_id}", response_model=DeviceResponse)
def get_device(
    device_id: str,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """Get device details"""
    device = DeviceService.get_device_by_device_id(db, device_id)

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )

    # Verify ownership
    if device.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return device


@router.patch("/{device_id}/status", response_model=DeviceResponse)
def update_device_status(
    device_id: str,
    status_update: DeviceStatusUpdate,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """Update device status"""
    device = DeviceService.get_device_by_device_id(db, device_id)

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )

    if device.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    try:
        updated_device = DeviceService.update_device_status(
            db,
            device_id,
            status_update.status,
            os_type=status_update.os_type
        )
        return updated_device
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{device_id}/stats")
def get_device_stats(
    device_id: str,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """Get device statistics"""
    device = DeviceService.get_device_by_device_id(db, device_id)

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )

    if device.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    stats = DeviceService.get_device_stats(db, device_id)
    return stats


@router.delete("/{device_id}")
def delete_device(
    device_id: str,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    """Delete a device"""
    device = DeviceService.get_device_by_device_id(db, device_id)

    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )

    if device.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    if DeviceService.delete_device(db, device_id):
        return {"message": "Device deleted successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete device"
        )
