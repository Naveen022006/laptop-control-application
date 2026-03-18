"""
FastAPI main application with WebSocket support
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
import json
import asyncio
from datetime import datetime
from app.database import init_db, get_db
from app.config import settings
from app.routes import auth, devices, commands
from app.services import manager, CommandService, DeviceService, AuthService
from app.utils import get_logger
from app.models import CommandStatus, DeviceStatus
from sqlalchemy.orm import Session

logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(devices.router)
app.include_router(commands.router)


# ==================== Startup/Shutdown ====================
@app.on_event("startup")
def startup_event():
    """Initialize database on startup"""
    init_db()
    logger.info("Application started")


@app.on_event("shutdown")
def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Application shutting down")


# ==================== Health Check ====================
@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": settings.ENVIRONMENT
    }


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Laptop Control API",
        "version": settings.API_VERSION,
        "status": "running"
    }


# ==================== WebSocket Endpoint ====================
@app.websocket("/ws/device/{device_id}")
async def websocket_endpoint(device_id: str, websocket: WebSocket, db: Session = Depends(get_db)):
    """
    WebSocket endpoint for laptop agents
    Handles real-time communication between backend and laptop agents
    """
    # Get device
    device = DeviceService.get_device_by_device_id(db, device_id)
    if not device:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        logger.warning(f"Unknown device attempted connection: {device_id}")
        return

    # Accept connection
    await manager.connect(device_id, websocket)

    # Update device status to online
    DeviceService.update_device_status(db, device_id, DeviceStatus.ONLINE)

    # Send any pending commands
    pending_commands = manager.get_pending_commands(device_id)
    for cmd in pending_commands:
        try:
            await websocket.send_json(cmd)
        except Exception as e:
            logger.error(f"Error sending pending command to {device_id}: {str(e)}")

    try:
        while True:
            # Receive message from device
            data = await websocket.receive_json()
            await handle_device_message(device_id, data, db)

    except WebSocketDisconnect:
        manager.disconnect(device_id)
        DeviceService.update_device_status(db, device_id, DeviceStatus.OFFLINE)
        logger.info(f"Device disconnected: {device_id}")

    except Exception as e:
        logger.error(f"WebSocket error for device {device_id}: {str(e)}")
        manager.disconnect(device_id)
        DeviceService.update_device_status(db, device_id, DeviceStatus.OFFLINE)


async def handle_device_message(device_id: str, data: dict, db: Session):
    """Handle messages from connected devices"""
    message_type = data.get("type")

    if message_type == "heartbeat":
        # Handle heartbeat
        await manager.handle_heartbeat_response(device_id)
        logger.debug(f"Heartbeat from device: {device_id}")

    elif message_type == "command_result":
        # Handle command execution result
        command_id = data.get("command_id")
        status = data.get("status")
        result = data.get("result")
        error_message = data.get("error_message")
        execution_time = data.get("execution_time", 0)

        if command_id:
            try:
                if status == "success":
                    CommandService.complete_command(
                        db,
                        command_id,
                        result,
                        execution_time
                    )
                    logger.info(f"Command completed: {command_id}")
                else:
                    CommandService.fail_command(
                        db,
                        command_id,
                        error_message or "Unknown error",
                        execution_time
                    )
                    logger.warning(f"Command failed: {command_id}")
            except Exception as e:
                logger.error(f"Error processing command result: {str(e)}")

    elif message_type == "status_update":
        # Handle device status update
        status = data.get("status")
        os_type = data.get("os_type")
        try:
            DeviceService.update_device_status(db, device_id, DeviceStatus[status.upper()], os_type)
            logger.info(f"Device status updated: {device_id} - {status}")
        except Exception as e:
            logger.error(f"Error updating device status: {str(e)}")

    else:
        logger.warning(f"Unknown message type from device {device_id}: {message_type}")


# ==================== WebSocket Monitoring Task ====================
@app.on_event("startup")
async def start_heartbeat_task():
    """Start background task for heartbeats"""
    asyncio.create_task(heartbeat_loop())


async def heartbeat_loop():
    """Send heartbeats to all connected devices"""
    while True:
        try:
            await asyncio.sleep(settings.WS_HEARTBEAT_INTERVAL)

            devices = manager.get_connected_devices()
            for device_id in devices:
                await manager.send_heartbeat(device_id)

        except Exception as e:
            logger.error(f"Error in heartbeat loop: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
