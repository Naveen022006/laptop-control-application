"""
Command routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import CommandRequest, CommandResponse, CommandStatus_
from app.services import CommandService, DeviceService, manager
from app.models import CommandStatus
from typing import List
import asyncio

router = APIRouter(prefix="/commands", tags=["Commands"])


@router.post("/", response_model=CommandResponse)
def send_command(
    command_req: CommandRequest,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(lambda: "user_id")
):
    """Send command to device"""
    # Verify device ownership
    device = DeviceService.get_device_by_device_id(db, command_req.device_id)

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
        # Create command
        command = CommandService.create_command(
            db,
            device_id=device.id,
            command_type=command_req.command_type,
            parameters=command_req.parameters
        )

        # Send to device via WebSocket
        message = {
            "type": "command",
            "command_id": command.id,
            "command_type": command.command_type,
            "parameters": command_req.parameters or {},
            "timestamp": command.sent_at.isoformat()
        }

        # Mark as sent if device is online
        device_online = manager.is_device_online(device.device_id)
        if device_online:
            # Send asynchronously
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(
                manager.send_to_device(device.device_id, message)
            )
            CommandService.mark_command_sent(db, command.id)

        return command

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{command_id}", response_model=CommandResponse)
def get_command_status(
    command_id: str,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(lambda: "user_id")
):
    """Get command status"""
    command = CommandService.get_command(db, command_id)

    if not command:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Command not found"
        )

    # Verify user owns the device
    if command.device.user_id != current_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )

    return command


@router.get("/device/{device_id}", response_model=List[CommandResponse])
def get_device_commands(
    device_id: str,
    limit: int = 50,
    status: str = None,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(lambda: "user_id")
):
    """Get commands for a device"""
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

    # Filter by status if provided
    status_filter = None
    if status:
        try:
            status_filter = CommandStatus[status.upper()]
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status: {status}"
            )

    commands = CommandService.get_device_commands(
        db,
        device.id,
        limit=limit,
        status_filter=status_filter
    )

    return commands


@router.get("/device/{device_id}/history", response_model=List[CommandResponse])
def get_command_history(
    device_id: str,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(lambda: "user_id")
):
    """Get command history for a device"""
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

    history = CommandService.get_command_history(db, device.id, limit)
    return history
