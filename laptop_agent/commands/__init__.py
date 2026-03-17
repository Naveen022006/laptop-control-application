"""
Initialize commands package.
"""
from .executor import (
    execute_command,
    get_command,
    COMMAND_REGISTRY,
    OpenChromeCommand,
    OpenWhatsAppCommand,
    ShutdownCommand,
    RestartCommand,
    TakeScreenshotCommand,
    SystemInfoCommand,
    RunScriptCommand
)

__all__ = [
    "execute_command",
    "get_command",
    "COMMAND_REGISTRY",
    "OpenChromeCommand",
    "OpenWhatsAppCommand",
    "ShutdownCommand",
    "RestartCommand",
    "TakeScreenshotCommand",
    "SystemInfoCommand",
    "RunScriptCommand"
]
