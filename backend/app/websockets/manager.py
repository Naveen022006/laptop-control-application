"""
WebSocket connection manager for handling laptop agent connections.
"""
from typing import Dict, Set
import logging
import asyncio
import json

logger = logging.getLogger("websocket_manager")


class WebSocketManager:
    """Manage WebSocket connections for laptop agents."""

    def __init__(self):
        self.active_connections: Dict[str, any] = {}
        self.connection_lock = asyncio.Lock()

    async def connect(self, device_id: str, websocket) -> None:
        """Register a new WebSocket connection."""
        async with self.connection_lock:
            self.active_connections[device_id] = websocket
            logger.info(f"Device {device_id} connected")

    async def disconnect(self, device_id: str) -> None:
        """Unregister a WebSocket connection."""
        async with self.connection_lock:
            if device_id in self.active_connections:
                del self.active_connections[device_id]
                logger.info(f"Device {device_id} disconnected")

    async def send_command(self, device_id: str, command: Dict) -> bool:
        """Send command to a connected device."""
        if device_id not in self.active_connections:
            logger.warning(f"Device {device_id} not connected")
            return False

        try:
            websocket = self.active_connections[device_id]
            await websocket.send_json(command)
            logger.info(f"Command sent to {device_id}: {command.get('command_name')}")
            return True
        except Exception as e:
            logger.error(f"Error sending command to {device_id}: {str(e)}")
            await self.disconnect(device_id)
            return False

    async def broadcast(self, message: Dict, exclude_device: str = None) -> None:
        """Broadcast message to all connected devices."""
        devices_to_remove = []

        for device_id, websocket in self.active_connections.items():
            if exclude_device and device_id == exclude_device:
                continue

            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to {device_id}: {str(e)}")
                devices_to_remove.append(device_id)

        # Clean up disconnected devices
        for device_id in devices_to_remove:
            await self.disconnect(device_id)

    def get_connected_devices(self) -> Dict[str, any]:
        """Get all connected devices."""
        return dict(self.active_connections)

    def is_device_connected(self, device_id: str) -> bool:
        """Check if a device is connected."""
        return device_id in self.active_connections


# Global WebSocket manager instance
ws_manager = WebSocketManager()
