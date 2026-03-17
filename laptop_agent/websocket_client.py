"""
WebSocket client for laptop agent communication with backend.
"""
import asyncio
import websockets
import json
import logging
import os
from typing import Callable, Optional
from datetime import datetime
import time

logger = logging.getLogger("websocket_client")


class WebSocketClient:
    """WebSocket client for communicating with backend server."""

    def __init__(self, server_url: str, api_token: str, on_command: Optional[Callable] = None):
        """
        Initialize WebSocket client.
        
        Args:
            server_url: Backend server URL (e.g., ws://localhost:8000)
            api_token: Device API token for authentication
            on_command: Callback function for handling commands
        """
        self.server_url = server_url
        self.api_token = api_token
        self.on_command = on_command
        self.websocket = None
        self.running = False
        self.reconnect_delay = 5  # seconds
        self.reconnect_max_delay = 30  # seconds

    async def connect(self) -> bool:
        """Connect to WebSocket server."""
        try:
            ws_url = f"{self.server_url}/ws/{self.api_token}"
            self.websocket = await websockets.connect(ws_url)
            self.running = True
            logger.info(f"Connected to WebSocket server: {ws_url}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to WebSocket: {str(e)}")
            return False

    async def disconnect(self):
        """Disconnect from WebSocket server."""
        self.running = False
        if self.websocket:
            await self.websocket.close()
            logger.info("Disconnected from WebSocket server")

    async def send_message(self, message: dict) -> bool:
        """Send message to server."""
        try:
            if not self.websocket or not self.running:
                return False
            
            await self.websocket.send(json.dumps(message))
            return True
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return False

    async def send_command_response(self, command_id: int, status: str, result: dict = None, error: str = None):
        """Send command execution response."""
        message = {
            "type": "command_response",
            "command_id": command_id,
            "status": status,
            "result": result,
            "error": error,
            "timestamp": datetime.utcnow().isoformat()
        }
        return await self.send_message(message)

    async def send_metrics(self, metrics: dict):
        """Send system metrics."""
        message = {
            "type": "system_metrics",
            "metrics": metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
        return await self.send_message(message)

    async def listen(self):
        """Listen for messages from server."""
        reconnect_delay = self.reconnect_delay
        
        while True:
            try:
                if not await self.connect():
                    await asyncio.sleep(reconnect_delay)
                    reconnect_delay = min(reconnect_delay * 2, self.reconnect_max_delay)
                    continue

                reconnect_delay = self.reconnect_delay  # Reset delay on successful connection

                while self.running and self.websocket:
                    try:
                        message = await asyncio.wait_for(self.websocket.recv(), timeout=60)
                        await self.handle_message(json.loads(message))
                    except asyncio.TimeoutError:
                        # Send ping to keep connection alive
                        await self.send_message({"type": "ping"})

            except websockets.exceptions.ConnectionClosed:
                logger.warning("WebSocket connection closed")
                await self.disconnect()
            except Exception as e:
                logger.error(f"WebSocket error: {str(e)}")
                await self.disconnect()

            if not self.running:
                break

            await asyncio.sleep(reconnect_delay)

    async def handle_message(self, message: dict):
        """Handle incoming message from server."""
        try:
            message_type = message.get("type")

            if message_type == "pong":
                logger.debug("Received pong")

            elif message_type == "command":
                command_id = message.get("id")
                command_name = message.get("command_name")
                command_params = message.get("command_params", {})

                logger.info(f"Received command: {command_name} (ID: {command_id})")

                if self.on_command:
                    await self.on_command(command_id, command_name, command_params)

            else:
                logger.warning(f"Unknown message type: {message_type}")

        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")


class WebSocketClientManager:
    """Manage WebSocket client with reconnection logic."""

    def __init__(self, server_url: str, api_token: str):
        self.client = None
        self.server_url = server_url
        self.api_token = api_token
        self.task = None

    def set_command_handler(self, handler: Callable):
        """Set handler for incoming commands."""
        self.client = WebSocketClient(
            self.server_url,
            self.api_token,
            on_command=handler
        )

    async def start(self):
        """Start WebSocket client."""
        if not self.client:
            raise RuntimeError("Command handler not set. Call set_command_handler first.")

        self.task = asyncio.create_task(self.client.listen())
        await self.task

    async def stop(self):
        """Stop WebSocket client."""
        if self.client:
            await self.client.disconnect()
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass

    async def send_command_response(self, command_id: int, status: str, result: dict = None, error: str = None):
        """Send command response."""
        if self.client:
            await self.client.send_command_response(command_id, status, result, error)

    async def send_metrics(self, metrics: dict):
        """Send system metrics."""
        if self.client:
            await self.client.send_metrics(metrics)
