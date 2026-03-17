"""
Initialize websockets package.
"""
from .manager import ws_manager
from . import routes

__all__ = ["ws_manager", "routes"]
