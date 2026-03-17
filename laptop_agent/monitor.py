"""
System monitoring utilities.
"""
import psutil
import logging
from typing import Dict, Any

logger = logging.getLogger("monitor")


class SystemMonitor:
    """Monitor system resources."""

    @staticmethod
    def get_cpu_usage() -> float:
        """Get CPU usage percentage."""
        return psutil.cpu_percent(interval=1)

    @staticmethod
    def get_memory_usage() -> Dict[str, Any]:
        """Get memory usage information."""
        mem = psutil.virtual_memory()
        return {
            "total": mem.total,
            "available": mem.available,
            "used": mem.used,
            "percent": mem.percent
        }

    @staticmethod
    def get_disk_usage(path: str = "/") -> Dict[str, Any]:
        """Get disk usage for a path."""
        disk = psutil.disk_usage(path)
        return {
            "total": disk.total,
            "used": disk.used,
            "free": disk.free,
            "percent": disk.percent
        }

    @staticmethod
    def get_battery_info() -> Dict[str, Any]:
        """Get battery information."""
        try:
            battery = psutil.sensors_battery()
            if battery:
                return {
                    "percent": battery.percent,
                    "is_charging": battery.power_plugged,
                    "time_left_sec": battery.secsleft
                }
            return None
        except Exception:
            return None

    @staticmethod
    def get_connected_processes() -> int:
        """Get number of processes."""
        return len(psutil.pids())

    @classmethod
    def get_system_metrics(cls) -> Dict[str, Any]:
        """Get all system metrics."""
        return {
            "cpu_percent": cls.get_cpu_usage(),
            "memory_percent": cls.get_memory_usage()["percent"],
            "disk_percent": cls.get_disk_usage()["percent"],
            "battery": cls.get_battery_info(),
            "process_count": cls.get_connected_processes()
        }


monitor = SystemMonitor()
