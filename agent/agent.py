"""
Laptop Control Agent - WebSocket Client
Connects to backend, listens for commands, and executes them locally
"""
import asyncio
import websockets
import json
import logging
import sys
import os
from datetime import datetime
import uuid
from typing import Dict, Any, Optional
from command_executor import CommandExecutor
from config import AgentConfig

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('agent.log')
    ]
)
logger = logging.getLogger(__name__)


class LaptopAgent:
    """Laptop Control Agent - WebSocket client for device control"""

    def __init__(self, config: AgentConfig):
        """Initialize agent"""
        self.config = config
        self.device_id = config.device_id
        self.backend_url = config.backend_url
        self.websocket = None
        self.connected = False
        self.executor = CommandExecutor()
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = config.max_reconnect_attempts

    async def connect(self) -> bool:
        """Connect to backend WebSocket"""
        try:
            ws_url = f"{self.backend_url}/ws/device/{self.device_id}"
            logger.info(f"Connecting to {ws_url}")

            self.websocket = await websockets.connect(ws_url)
            self.connected = True
            self.reconnect_attempts = 0
            logger.info(f"Connected to backend: {ws_url}")

            return True

        except Exception as e:
            logger.error(f"Connection failed: {str(e)}")
            self.connected = False
            return False

    async def disconnect(self):
        """Disconnect from backend"""
        if self.websocket:
            await self.websocket.close()
            self.connected = False
            logger.info("Disconnected from backend")

    async def run(self):
        """Main agent loop"""
        while True:
            try:
                # Connect if not connected
                if not self.connected:
                    if not await self.connect():
                        await asyncio.sleep(self.config.reconnect_delay)
                        continue

                # Listen for messages from backend
                try:
                    message = await asyncio.wait_for(
                        self.websocket.recv(),
                        timeout=self.config.message_timeout
                    )
                    await self.handle_message(message)

                except asyncio.TimeoutError:
                    # Timeout occurred, send heartbeat response
                    logger.debug("Message timeout - sending heartbeat response")
                    await self.send_heartbeat_response()

            except websockets.exceptions.ConnectionClosed:
                logger.warning("Connection closed by server")
                self.connected = False
                self.reconnect_attempts += 1

                if self.reconnect_attempts >= self.max_reconnect_attempts:
                    logger.error(f"Max reconnection attempts ({self.max_reconnect_attempts}) reached")
                    await asyncio.sleep(self.config.reconnect_delay * 2)
                    self.reconnect_attempts = 0
                else:
                    await asyncio.sleep(self.config.reconnect_delay)

            except Exception as e:
                logger.error(f"Error in agent loop: {str(e)}")
                self.connected = False
                await asyncio.sleep(self.config.reconnect_delay)

    async def handle_message(self, message_str: str):
        """Handle incoming message from backend"""
        try:
            data = json.loads(message_str)
            message_type = data.get("type")

            logger.info(f"Received message type: {message_type}")

            if message_type == "command":
                await self.handle_command(data)

            elif message_type == "heartbeat":
                await self.send_heartbeat_response()

            elif message_type == "status_request":
                await self.send_status()

            else:
                logger.warning(f"Unknown message type: {message_type}")

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON message: {str(e)}")
        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")

    async def handle_command(self, data: dict):
        """Handle command execution"""
        command_id = data.get("command_id")
        command_type = data.get("command_type")
        parameters = data.get("parameters", {})

        logger.info(f"Executing command: {command_type} (ID: {command_id})")

        start_time = datetime.utcnow()

        try:
            # Execute command
            result = await self.executor.execute(command_type, parameters)

            execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)

            # Send success result
            await self.send_command_result(
                command_id,
                "success",
                result=result,
                execution_time=execution_time
            )

            logger.info(f"Command executed successfully: {command_type} ({command_id})")

        except Exception as e:
            execution_time = int((datetime.utcnow() - start_time).total_seconds() * 1000)

            # Send error result
            await self.send_command_result(
                command_id,
                "failed",
                error_message=str(e),
                execution_time=execution_time
            )

            logger.error(f"Command execution failed: {command_type} ({command_id}) - {str(e)}")

    async def send_command_result(
        self,
        command_id: str,
        status: str,
        result=None,
        error_message: Optional[str] = None,
        execution_time: int = 0
    ):
        """Send command execution result back to backend"""
        try:
            message = {
                "type": "command_result",
                "command_id": command_id,
                "status": status,
                "result": result,
                "error_message": error_message,
                "execution_time": execution_time,
                "timestamp": datetime.utcnow().isoformat()
            }

            if self.connected and self.websocket:
                await self.websocket.send(json.dumps(message))
                logger.debug(f"Result sent for command: {command_id}")

        except Exception as e:
            logger.error(f"Error sending command result: {str(e)}")

    async def send_heartbeat_response(self):
        """Send heartbeat response to backend"""
        try:
            message = {
                "type": "heartbeat",
                "device_id": self.device_id,
                "timestamp": datetime.utcnow().isoformat()
            }

            if self.connected and self.websocket:
                await self.websocket.send(json.dumps(message))
                logger.debug("Heartbeat sent")

        except Exception as e:
            logger.error(f"Error sending heartbeat: {str(e)}")

    async def send_status(self):
        """Send device status to backend"""
        try:
            system_info = self.executor.get_system_info()

            message = {
                "type": "status_update",
                "device_id": self.device_id,
                "status": "online",
                "system_info": system_info,
                "timestamp": datetime.utcnow().isoformat()
            }

            if self.connected and self.websocket:
                await self.websocket.send(json.dumps(message))
                logger.debug("Status sent")

        except Exception as e:
            logger.error(f"Error sending status: {str(e)}")


async def main():
    """Main entry point"""
    config = AgentConfig()
    agent = LaptopAgent(config)

    try:
        logger.info(f"Starting Laptop Control Agent: {config.device_id}")
        await agent.run()
    except KeyboardInterrupt:
        logger.info("Shutting down agent...")
        await agent.disconnect()
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        await agent.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
