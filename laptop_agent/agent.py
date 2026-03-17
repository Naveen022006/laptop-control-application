"""
Laptop control agent main application.
"""
import asyncio
import logging
import os
import signal
import sys
from datetime import datetime
from dotenv import load_dotenv

from commands import execute_command
from monitor import monitor
from websocket_client import WebSocketClientManager

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("agent")


class LaptopAgent:
    """Main laptop control agent."""

    def __init__(self):
        """Initialize agent."""
        self.server_url = os.getenv("BACKEND_URL", "ws://localhost:8000")
        self.device_id = os.getenv("DEVICE_ID", "laptop-001")
        self.api_token = os.getenv("API_TOKEN", "")
        self.metrics_interval = int(os.getenv("METRICS_INTERVAL", "30"))  # seconds

        if not self.api_token:
            raise ValueError("API_TOKEN environment variable must be set")

        self.ws_manager = WebSocketClientManager(self.server_url, self.api_token)
        self.running = False
        self.metrics_task = None

    async def handle_command(self, command_id: int, command_name: str, command_params: dict):
        """Handle command from backend."""
        try:
            logger.info(f"Handling command: {command_name} (ID: {command_id})")

            # Execute command
            result = execute_command(command_name, command_params)

            # Send response
            status = "completed" if result.get("success") else "failed"
            await self.ws_manager.send_command_response(
                command_id,
                status,
                result=result.get("result"),
                error=result.get("error")
            )

            logger.info(f"Command response sent: {command_name} (ID: {command_id}, Status: {status})")

        except Exception as e:
            logger.error(f"Error handling command: {str(e)}")
            await self.ws_manager.send_command_response(
                command_id,
                "failed",
                error=str(e)
            )

    async def send_metrics(self):
        """Periodically send system metrics to backend."""
        while self.running:
            try:
                metrics = monitor.get_system_metrics()
                await self.ws_manager.send_metrics(metrics)
                logger.debug(f"Metrics sent: CPU={metrics['cpu_percent']}%, Memory={metrics['memory_percent']}%")

                await asyncio.sleep(self.metrics_interval)

            except Exception as e:
                logger.error(f"Error sending metrics: {str(e)}")
                await asyncio.sleep(5)

    async def start(self):
        """Start the agent."""
        try:
            logger.info(f"Starting Laptop Control Agent")
            logger.info(f"Device ID: {self.device_id}")
            logger.info(f"Backend URL: {self.server_url}")

            self.running = True

            # Set command handler
            self.ws_manager.set_command_handler(self.handle_command)

            # Start metrics task
            self.metrics_task = asyncio.create_task(self.send_metrics())

            # Start WebSocket client
            await self.ws_manager.start()

        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
            await self.stop()
        except Exception as e:
            logger.error(f"Agent error: {str(e)}")
            await self.stop()

    async def stop(self):
        """Stop the agent."""
        logger.info("Stopping Laptop Control Agent")
        self.running = False

        if self.metrics_task:
            self.metrics_task.cancel()
            try:
                await self.metrics_task
            except asyncio.CancelledError:
                pass

        await self.ws_manager.stop()
        logger.info("Agent stopped")
        sys.exit(0)

    def handle_signal(self, signum, frame):
        """Handle system signals."""
        logger.info(f"Received signal: {signum}")
        asyncio.create_task(self.stop())


async def main():
    """Main entry point."""
    agent = LaptopAgent()

    # Register signal handlers
    signal.signal(signal.SIGINT, agent.handle_signal)
    signal.signal(signal.SIGTERM, agent.handle_signal)

    await agent.start()


if __name__ == "__main__":
    asyncio.run(main())
