"""
Command execution routes.
"""
from fastapi import APIRouter, HTTPException, Depends, status, Header
from sqlalchemy.orm import Session
from datetime import datetime
import json

from ..models.database import get_db
from ..models.models import Device, Command, CommandStatus
from ..schemas.schemas import CommandRequest, CommandResponse
from ..websockets.manager import ws_manager
from ..utils.helpers import convert_dict_to_json, convert_json_to_dict, calculate_execution_time
from ..utils.logger import root_logger

router = APIRouter(prefix="/commands", tags=["commands"])
logger = root_logger


def verify_api_token(api_token: str, db: Session) -> Device:
    """Verify API token and return device."""
    device = db.query(Device).filter(Device.api_token == api_token).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API token"
        )
    if not device.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Device is inactive"
        )
    return device


@router.post("/execute/{target_device_id}", response_model=CommandResponse)
async def execute_command(
    target_device_id: str,
    command_data: CommandRequest,
    authorization: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    Execute a command on a target device (laptop).
    
    The command is sent to the laptop agent via WebSocket and queued until execution.
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authorization header"
        )

    # Extract token from "Bearer <token>"
    try:
        token = authorization.split(" ")[1] if " " in authorization else authorization
    except IndexError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )

    # Verify source device (mobile app)
    source_device = verify_api_token(token, db)

    # Verify target device exists and is active
    target_device = db.query(Device).filter(Device.device_id == target_device_id).first()
    if not target_device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target device not found"
        )

    if target_device.device_type != "laptop":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Target device must be a laptop"
        )

    # Create command record
    command = Command(
        device_id=target_device_id,
        command_name=command_data.command_name,
        command_params=convert_dict_to_json(command_data.command_params) if command_data.command_params else None,
        status=CommandStatus.PENDING
    )

    db.add(command)
    db.commit()
    db.refresh(command)

    logger.info(f"Command created: ID={command.id}, Device={target_device_id}, Command={command_data.command_name}")

    # Send command to device if connected
    command_dict = {
        "type": "command",
        "id": command.id,
        "command_name": command_data.command_name,
        "command_params": convert_json_to_dict(command.command_params) if command.command_params else {}
    }

    if ws_manager.is_device_connected(target_device_id):
        try:
            await ws_manager.send_command(target_device_id, command_dict)
            command.status = CommandStatus.EXECUTING
            db.commit()
            logger.info(f"Command sent via WebSocket: ID={command.id}")
        except Exception as e:
            logger.error(f"Failed to send command via WebSocket: {str(e)}")
    else:
        logger.warning(f"Target device {target_device_id} not connected. Command queued.")

    return command


@router.get("/history/{device_id}", response_model=list[CommandResponse])
def get_command_history(
    device_id: str,
    limit: int = 50,
    offset: int = 0,
    api_token: str = Header(None),
    db: Session = Depends(get_db)
):
    """Get command execution history for a device."""
    if not api_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API token"
        )

    verify_api_token(api_token, db)

    commands = db.query(Command).filter(
        Command.device_id == device_id
    ).order_by(
        Command.created_at.desc()
    ).offset(offset).limit(limit).all()

    return commands


@router.get("/{command_id}", response_model=CommandResponse)
def get_command(
    command_id: int,
    api_token: str = Header(None),
    db: Session = Depends(get_db)
):
    """Get command details."""
    if not api_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API token"
        )

    verify_api_token(api_token, db)

    command = db.query(Command).filter(Command.id == command_id).first()
    if not command:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Command not found"
        )

    return command
