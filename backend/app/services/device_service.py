"""
Device service for device management
"""
from sqlalchemy.orm import Session
from app.models import Device, DeviceStatus, User
from app.utils.logger import get_logger
from typing import Optional
from datetime import datetime

logger = get_logger(__name__)


class DeviceService:
    """Service for device management"""

    @staticmethod
    def register_device(
        db: Session,
        user_id: str,
        device_id: str,
        name: str,
        device_type: str = "laptop",
        os_type: Optional[str] = None
    ) -> Device:
        """Register a new device"""
        # Verify user exists
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise ValueError(f"User not found: {user_id}")

        # Check if device already registered
        existing_device = db.query(Device).filter(
            Device.device_id == device_id,
            Device.user_id == user_id
        ).first()

        if existing_device:
            logger.info(f"Device already registered: {device_id}")
            return existing_device

        # Create new device
        device = Device(
            device_id=device_id,
            user_id=user_id,
            name=name,
            device_type=device_type,
            os_type=os_type,
            status=DeviceStatus.OFFLINE
        )

        db.add(device)
        db.commit()
        db.refresh(device)

        logger.info(f"Device registered: {device_id} ({name})")
        return device

    @staticmethod
    def get_device(db: Session, device_id: str) -> Optional[Device]:
        """Get device by ID"""
        return db.query(Device).filter(Device.id == device_id).first()

    @staticmethod
    def get_device_by_device_id(db: Session, device_id: str) -> Optional[Device]:
        """Get device by device_id"""
        return db.query(Device).filter(Device.device_id == device_id).first()

    @staticmethod
    def get_user_devices(db: Session, user_id: str) -> list:
        """Get all devices for a user"""
        return db.query(Device).filter(
            Device.user_id == user_id,
            Device.is_active == True
        ).all()

    @staticmethod
    def update_device_status(
        db: Session,
        device_id: str,
        status: DeviceStatus,
        os_type: Optional[str] = None
    ) -> Device:
        """Update device status"""
        device = db.query(Device).filter(Device.device_id == device_id).first()
        if not device:
            raise ValueError(f"Device not found: {device_id}")

        device.status = status
        device.last_seen = datetime.utcnow()

        if os_type:
            device.os_type = os_type

        db.commit()
        db.refresh(device)

        logger.info(f"Device status updated: {device_id} - Status: {status}")
        return device

    @staticmethod
    def update_device_last_seen(db: Session, device_id: str) -> Device:
        """Update device last_seen timestamp"""
        device = db.query(Device).filter(Device.device_id == device_id).first()
        if device:
            device.last_seen = datetime.utcnow()
            db.commit()
            db.refresh(device)
        return device

    @staticmethod
    def deactivate_device(db: Session, device_id: str) -> Device:
        """Deactivate a device"""
        device = db.query(Device).filter(Device.device_id == device_id).first()
        if not device:
            raise ValueError(f"Device not found: {device_id}")

        device.is_active = False
        device.status = DeviceStatus.OFFLINE
        db.commit()
        db.refresh(device)

        logger.info(f"Device deactivated: {device_id}")
        return device

    @staticmethod
    def get_device_stats(db: Session, device_id: str) -> dict:
        """Get device statistics"""
        device = db.query(Device).filter(Device.device_id == device_id).first()
        if not device:
            return {}

        command_count = len(device.commands)
        completed_commands = sum(1 for cmd in device.commands if cmd.status.value == "completed")
        failed_commands = sum(1 for cmd in device.commands if cmd.status.value == "failed")

        return {
            "device_id": device.device_id,
            "device_name": device.name,
            "status": device.status.value,
            "total_commands": command_count,
            "completed_commands": completed_commands,
            "failed_commands": failed_commands,
            "last_seen": device.last_seen,
            "created_at": device.created_at,
        }

    @staticmethod
    def delete_device(db: Session, device_id: str) -> bool:
        """Delete a device"""
        device = db.query(Device).filter(Device.device_id == device_id).first()
        if not device:
            return False

        db.delete(device)
        db.commit()
        logger.info(f"Device deleted: {device_id}")
        return True
