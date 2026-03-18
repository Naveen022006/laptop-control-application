"""
Command service for managing command execution
"""
from sqlalchemy.orm import Session
from app.models import Command, CommandStatus, Device
from app.utils.logger import get_logger
from datetime import datetime
from typing import Optional
import json
import uuid

logger = get_logger(__name__)


class CommandService:
    """Service for managing command execution"""

    @staticmethod
    def create_command(
        db: Session,
        device_id: str,
        command_type: str,
        parameters: Optional[dict] = None
    ) -> Command:
        """Create a new command"""
        # Verify device exists
        device = db.query(Device).filter(Device.id == device_id).first()
        if not device:
            raise ValueError(f"Device not found: {device_id}")

        # Create command
        command = Command(
            device_id=device_id,
            command_type=command_type,
            parameters=json.dumps(parameters) if parameters else None,
            status=CommandStatus.PENDING
        )

        db.add(command)
        db.commit()
        db.refresh(command)

        logger.info(f"Command created: {command.id} ({command_type}) for device: {device_id}")
        return command

    @staticmethod
    def get_command(db: Session, command_id: str) -> Optional[Command]:
        """Get command by ID"""
        return db.query(Command).filter(Command.id == command_id).first()

    @staticmethod
    def update_command_status(
        db: Session,
        command_id: str,
        status: CommandStatus,
        result: Optional[any] = None,
        error_message: Optional[str] = None,
        execution_time: Optional[int] = None
    ) -> Command:
        """Update command status and result"""
        command = db.query(Command).filter(Command.id == command_id).first()
        if not command:
            raise ValueError(f"Command not found: {command_id}")

        command.status = status
        command.executed_at = datetime.utcnow()

        if result is not None:
            command.result = json.dumps(result) if not isinstance(result, str) else result

        if error_message:
            command.error_message = error_message

        if execution_time is not None:
            command.execution_time = execution_time

        db.commit()
        db.refresh(command)

        logger.info(f"Command updated: {command_id} - Status: {status}")
        return command

    @staticmethod
    def get_device_commands(
        db: Session,
        device_id: str,
        limit: int = 50,
        status_filter: Optional[CommandStatus] = None
    ) -> list:
        """Get commands for a device"""
        query = db.query(Command).filter(Command.device_id == device_id)

        if status_filter:
            query = query.filter(Command.status == status_filter)

        return query.order_by(Command.created_at.desc()).limit(limit).all()

    @staticmethod
    def get_pending_commands(db: Session, device_id: str) -> list:
        """Get pending commands for a device"""
        return db.query(Command).filter(
            Command.device_id == device_id,
            Command.status == CommandStatus.PENDING
        ).order_by(Command.created_at.asc()).all()

    @staticmethod
    def mark_command_sent(db: Session, command_id: str) -> Command:
        """Mark command as sent to device"""
        command = db.query(Command).filter(Command.id == command_id).first()
        if command:
            command.status = CommandStatus.SENT
            db.commit()
            db.refresh(command)
            logger.info(f"Command marked as sent: {command_id}")
        return command

    @staticmethod
    def mark_command_executing(db: Session, command_id: str) -> Command:
        """Mark command as executing"""
        command = db.query(Command).filter(Command.id == command_id).first()
        if command:
            command.status = CommandStatus.EXECUTING
            db.commit()
            db.refresh(command)
            logger.info(f"Command marked as executing: {command_id}")
        return command

    @staticmethod
    def complete_command(
        db: Session,
        command_id: str,
        result: any,
        execution_time: int
    ) -> Command:
        """Mark command as completed with result"""
        return CommandService.update_command_status(
            db,
            command_id,
            CommandStatus.COMPLETED,
            result=result,
            execution_time=execution_time
        )

    @staticmethod
    def fail_command(
        db: Session,
        command_id: str,
        error_message: str,
        execution_time: Optional[int] = None
    ) -> Command:
        """Mark command as failed"""
        return CommandService.update_command_status(
            db,
            command_id,
            CommandStatus.FAILED,
            error_message=error_message,
            execution_time=execution_time
        )

    @staticmethod
    def get_command_history(
        db: Session,
        device_id: str,
        limit: int = 100
    ) -> list:
        """Get command history for a device"""
        return db.query(Command).filter(
            Command.device_id == device_id
        ).order_by(
            Command.created_at.desc()
        ).limit(limit).all()

    @staticmethod
    def cleanup_old_commands(db: Session, days: int = 30) -> int:
        """Delete commands older than specified days"""
        from datetime import timedelta

        cutoff_date = datetime.utcnow() - timedelta(days=days)
        deleted_count = db.query(Command).filter(
            Command.created_at < cutoff_date
        ).delete()

        db.commit()
        logger.info(f"Deleted {deleted_count} old commands (older than {days} days)")
        return deleted_count
