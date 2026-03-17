"""
Main FastAPI application setup and configuration.
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from contextlib import asynccontextmanager

from .models.database import create_tables
from .routes import devices, commands, metrics
from .websockets import routes as ws_routes
from .utils.logger import root_logger

logger = root_logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup/shutdown events.
    """
    # Startup
    logger.info("Starting Laptop Control Backend")
    create_tables()
    logger.info("Database tables created/verified")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Laptop Control Backend")


# Create FastAPI app
app = FastAPI(
    title="Laptop Control API",
    description="Remote Laptop Control System Backend",
    version="1.0.0",
    lifespan=lifespan
)

# CORS settings
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(devices.router)
app.include_router(commands.router)
app.include_router(metrics.router)
app.include_router(ws_routes.router)


# Health check endpoint
@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "message": "Laptop Control Backend is running"
    }


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Laptop Control API",
        "version": "1.0.0",
        "description": "Remote Laptop Control System Backend",
        "endpoints": {
            "health": "/health",
            "docs": "/docs",
            "device_management": "/devices",
            "command_execution": "/commands",
            "system_metrics": "/metrics",
            "websocket": "/ws/{api_token}"
        }
    }


# Exception handlers
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
