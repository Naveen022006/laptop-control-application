"""
System metrics and monitoring routes.
"""
from fastapi import APIRouter, HTTPException, Depends, status, Header
from sqlalchemy.orm import Session
from datetime import datetime

from ..models.database import get_db
from ..models.models import Device, SystemMetrics
from ..schemas.schemas import SystemMetricsRequest, SystemMetricsResponse
from ..utils.logger import root_logger

router = APIRouter(prefix="/metrics", tags=["metrics"])
logger = root_logger


@router.post("/", response_model=SystemMetricsResponse, status_code=status.HTTP_201_CREATED)
def record_metrics(
    metrics_data: SystemMetricsRequest,
    device_id: str = Header(None),
    api_token: str = Header(None),
    db: Session = Depends(get_db)
):
    """
    Record system metrics from a device.
    
    This endpoint is called by the laptop agent to report system metrics.
    """
    if not device_id or not api_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required headers: device_id, api_token"
        )

    # Verify device
    device = db.query(Device).filter(
        Device.device_id == device_id,
        Device.api_token == api_token
    ).first()

    if not device:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid device credentials"
        )

    # Create metrics record
    metrics = SystemMetrics(
        device_id=device_id,
        cpu_percent=metrics_data.cpu_percent,
        memory_percent=metrics_data.memory_percent,
        disk_percent=metrics_data.disk_percent,
        temperature=metrics_data.temperature,
        battery_percent=metrics_data.battery_percent,
        is_charging=metrics_data.is_charging
    )

    db.add(metrics)
    
    # Update device last_online
    device.last_online = datetime.utcnow()
    
    db.commit()
    db.refresh(metrics)

    logger.debug(f"Metrics recorded for {device_id}: CPU={metrics_data.cpu_percent}%, Memory={metrics_data.memory_percent}%")
    return metrics


@router.get("/{device_id}/latest", response_model=SystemMetricsResponse)
def get_latest_metrics(
    device_id: str,
    api_token: str = Header(None),
    db: Session = Depends(get_db)
):
    """Get latest system metrics for a device."""
    if not api_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API token"
        )

    # Verify API token
    device = db.query(Device).filter(Device.api_token == api_token).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API token"
        )

    metrics = db.query(SystemMetrics).filter(
        SystemMetrics.device_id == device_id
    ).order_by(SystemMetrics.created_at.desc()).first()

    if not metrics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No metrics found for device"
        )

    return metrics


@router.get("/{device_id}/history")
def get_metrics_history(
    device_id: str,
    limit: int = 100,
    api_token: str = Header(None),
    db: Session = Depends(get_db)
):
    """Get metrics history for a device."""
    if not api_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing API token"
        )

    # Verify API token
    device = db.query(Device).filter(Device.api_token == api_token).first()
    if not device:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API token"
        )

    metrics = db.query(SystemMetrics).filter(
        SystemMetrics.device_id == device_id
    ).order_by(SystemMetrics.created_at.desc()).limit(limit).all()

    return metrics
