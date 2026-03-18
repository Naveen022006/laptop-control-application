"""
WebSocket manager for handling device connections
"""
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from app.models import Device, DeviceStatus
from app.utils.logger import get_logger
import asyncio
import json
from typing import Dict, Set
from datetime import datetime

logger = get_logger(__name__)


class ConnectionManager:
    """Manages WebSocket connections for devices"""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.device_meta: Dict[str, Dict] = {}  # Store device metadata
        self.pending_commands: Dict[str, list] = {}  # Command queue for offline devices

    async def connect(self, device_id: str, websocket: WebSocket):
        """Accept and register a device connection"""
        await websocket.accept()
        self.active_connections[device_id] = websocket
        self.device_meta[device_id] = {
            "connected_at": datetime.utcnow(),
            "last_heartbeat": datetime.utcnow(),
            "status": "connected"
        }
        logger.info(f"Device connected: {device_id}")

    def disconnect(self, device_id: str):
        """Disconnect a device"""
        if device_id in self.active_connections:
            del self.active_connections[device_id]
            self.device_meta[device_id]["status"] = "disconnected"
            logger.info(f"Device disconnected: {device_id}")

    async def send_to_device(
        self,
        device_id: str,
        message: dict
    ) -> bool:
        """Send message to a connected device"""
        if device_id not in self.active_connections:
            # Queue message for offline device
            if device_id not in self.pending_commands:
                self.pending_commands[device_id] = []
            self.pending_commands[device_id].append(message)
            logger.info(f"Message queued for offline device: {device_id}")
            return False

        try:
            websocket = self.active_connections[device_id]
            await websocket.send_json(message)
            logger.debug(f"Message sent to device {device_id}: {message['type']}")
            return True
        except Exception as e:
            logger.error(f"Error sending message to device {device_id}: {str(e)}")
            self.disconnect(device_id)
            return False

    async def receive_from_device(self, device_id: str) -> dict:
        """Receive message from a connected device"""
        if device_id not in self.active_connections:
            return None

        try:
            websocket = self.active_connections[device_id]
            data = await websocket.receive_json()
            return data
        except WebSocketDisconnect:
            self.disconnect(device_id)
            return None
        except Exception as e:
            logger.error(f"Error receiving from device {device_id}: {str(e)}")
            self.disconnect(device_id)
            return None

    async def broadcast_to_all_devices(self, message: dict, exclude_device: str = None):
        """Broadcast message to all connected devices"""
        disconnected = []

        for device_id, connection in self.active_connections.items():
            if exclude_device and device_id == exclude_device:
                continue

            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to device {device_id}: {str(e)}")
                disconnected.append(device_id)

        for device_id in disconnected:
            self.disconnect(device_id)

    def get_pending_commands(self, device_id: str) -> list:
        """Get pending commands for a device"""
        commands = self.pending_commands.get(device_id, [])
        if device_id in self.pending_commands:
            del self.pending_commands[device_id]
        return commands

    def is_device_online(self, device_id: str) -> bool:
        """Check if a device is online"""
        return device_id in self.active_connections

    def get_connected_devices(self) -> list:
        """Get list of connected device IDs"""
        return list(self.active_connections.keys())

    def get_device_status(self, device_id: str) -> dict:
        """Get device connection status"""
        return self.device_meta.get(device_id, {})

    async def send_heartbeat(self, device_id: str) -> bool:
        """Send heartbeat to device"""
        heartbeat_message = {
            "type": "heartbeat",
            "timestamp": datetime.utcnow().isoformat()
        }
        return await self.send_to_device(device_id, heartbeat_message)

    async def handle_heartbeat_response(self, device_id: str):
        """Update heartbeat timestamp for device"""
        if device_id in self.device_meta:
            self.device_meta[device_id]["last_heartbeat"] = datetime.utcnow()


# Global connection manager instance
manager = ConnectionManager()
