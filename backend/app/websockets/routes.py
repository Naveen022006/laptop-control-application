"""
WebSocket route handlers.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, status
from sqlalchemy.orm import Session
import json
import logging

from ..models.database import get_db
from ..models.models import Device
from .manager import ws_manager

router = APIRouter(prefix="/ws", tags=["websocket"])
logger = logging.getLogger("websocket_routes")


@router.websocket("/ws/{api_token}")
async def websocket_endpoint(websocket: WebSocket, api_token: str, db: Session = Depends(get_db)):
    """
    WebSocket endpoint for laptop agents.
    
    The laptop agent connects with its API token to receive and execute commands.
    """
    # Verify device authentication
    device = db.query(Device).filter(Device.api_token == api_token).first()
    
    if not device:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
        logger.warning(f"WebSocket connection rejected: Invalid token")
        return

    if not device.is_active:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Device inactive")
        logger.warning(f"WebSocket connection rejected: Device {device.device_id} inactive")
        return

    await websocket.accept()
    await ws_manager.connect(device.device_id, websocket)
    logger.info(f"WebSocket connection established for device: {device.device_id}")

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            message_type = data.get("type")

            if message_type == "ping":
                # Respond to ping to keep connection alive
                await websocket.send_json({"type": "pong", "timestamp": json.dumps({"ms": 0}, default=str)})

            elif message_type == "command_response":
                # Handle command execution response from agent
                command_id = data.get("command_id")
                status_msg = data.get("status")
                result = data.get("result")
                error = data.get("error")

                logger.info(f"Command response from {device.device_id}: ID={command_id}, Status={status_msg}")

            elif message_type == "system_metrics":
                # Handle system metrics update
                metrics = data.get("metrics", {})
                logger.debug(f"System metrics from {device.device_id}: {metrics}")

            else:
                logger.warning(f"Unknown message type from {device.device_id}: {message_type}")

    except WebSocketDisconnect:
        await ws_manager.disconnect(device.device_id)
        logger.info(f"WebSocket disconnected for device: {device.device_id}")
    except Exception as e:
        logger.error(f"WebSocket error for device {device.device_id}: {str(e)}")
        await ws_manager.disconnect(device.device_id)
