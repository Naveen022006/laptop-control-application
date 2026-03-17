"""
Concrete command implementations.
"""
import subprocess
import platform
import os
import json
import logging
from typing import Dict, Any
from .base import BaseCommand, CommandResult

logger = logging.getLogger("commands")


class OpenChromeCommand(BaseCommand):
    """Open Google Chrome."""

    def execute(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        try:
            url = (params.get("url", "") if params else "") or "https://www.google.com"
            
            system = platform.system()
            
            if system == "Windows":
                os.startfile(f'http://{url}' if not url.startswith(('http://', 'https://')) else url)
            elif system == "Darwin":  # macOS
                subprocess.Popen(['open', '-a', 'Google Chrome', url])
            else:  # Linux
                subprocess.Popen(['google-chrome', url])
            
            result = CommandResult(
                success=True,
                result={"message": f"Chrome opened with URL: {url}"}
            )
        except Exception as e:
            result = CommandResult(success=False, error=f"Failed to open Chrome: {str(e)}")
        
        return result.to_dict()


class OpenWhatsAppCommand(BaseCommand):
    """Open WhatsApp."""

    def execute(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        try:
            system = platform.system()
            
            if system == "Windows":
                # Try to open WhatsApp from Start Menu
                subprocess.Popen(['start', 'WhatsApp'], shell=True)
            elif system == "Darwin":  # macOS
                subprocess.Popen(['open', '-a', 'WhatsApp'])
            else:  # Linux
                subprocess.Popen(['whatsapp-nativefier'])
            
            result = CommandResult(
                success=True,
                result={"message": "WhatsApp opened"}
            )
        except Exception as e:
            result = CommandResult(success=False, error=f"Failed to open WhatsApp: {str(e)}")
        
        return result.to_dict()


class ShutdownCommand(BaseCommand):
    """Shutdown the system."""

    def execute(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        try:
            delay = (params.get("delay", 0) if params else 0)  # seconds
            
            system = platform.system()
            
            if system == "Windows":
                cmd = f"shutdown /s /t {delay}"
            elif system == "Darwin":  # macOS
                cmd = f"osascript -e 'tell application \"System Events\" to shut down'"
            else:  # Linux
                cmd = f"shutdown -h {delay}"
            
            subprocess.Popen(cmd, shell=True)
            
            result = CommandResult(
                success=True,
                result={"message": f"System shutdown initiated (delay: {delay}s)"}
            )
        except Exception as e:
            result = CommandResult(success=False, error=f"Failed to shutdown: {str(e)}")
        
        return result.to_dict()


class RestartCommand(BaseCommand):
    """Restart the system."""

    def execute(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        try:
            delay = (params.get("delay", 0) if params else 0)  # seconds
            
            system = platform.system()
            
            if system == "Windows":
                cmd = f"shutdown /r /t {delay}"
            elif system == "Darwin":  # macOS
                cmd = f"osascript -e 'tell application \"System Events\" to restart'"
            else:  # Linux
                cmd = f"shutdown -r {delay}"
            
            subprocess.Popen(cmd, shell=True)
            
            result = CommandResult(
                success=True,
                result={"message": f"System restart initiated (delay: {delay}s)"}
            )
        except Exception as e:
            result = CommandResult(success=False, error=f"Failed to restart: {str(e)}")
        
        return result.to_dict()


class TakeScreenshotCommand(BaseCommand):
    """Take a screenshot."""

    def execute(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        try:
            from PIL import ImageGrab
            
            # Take screenshot
            screenshot = ImageGrab.grab()
            
            # Save to file
            os.makedirs("screenshots", exist_ok=True)
            filename = f"screenshots/screenshot_{int(__import__('time').time())}.png"
            screenshot.save(filename)
            
            result = CommandResult(
                success=True,
                result={"message": "Screenshot saved", "path": filename}
            )
        except Exception as e:
            result = CommandResult(success=False, error=f"Failed to take screenshot: {str(e)}")
        
        return result.to_dict()


class SystemInfoCommand(BaseCommand):
    """Get system information."""

    def execute(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        try:
            import psutil
            
            system_info = {
                "platform": platform.system(),
                "platform_version": platform.version(),
                "processor": platform.processor(),
                "cpu_count": psutil.cpu_count(),
                "cpu_percent": psutil.cpu_percent(interval=1),
                "memory": {
                    "total": str(psutil.virtual_memory().total // (1024 ** 3)) + " GB",
                    "available": str(psutil.virtual_memory().available // (1024 ** 3)) + " GB",
                    "used": str(psutil.virtual_memory().used // (1024 ** 3)) + " GB",
                    "percent": psutil.virtual_memory().percent
                },
                "disk": {
                    "total": str(psutil.disk_usage('/').total // (1024 ** 3)) + " GB",
                    "used": str(psutil.disk_usage('/').used // (1024 ** 3)) + " GB",
                    "free": str(psutil.disk_usage('/').free // (1024 ** 3)) + " GB",
                    "percent": psutil.disk_usage('/').percent
                }
            }
            
            result = CommandResult(success=True, result=system_info)
        except Exception as e:
            result = CommandResult(success=False, error=f"Failed to get system info: {str(e)}")
        
        return result.to_dict()


class RunScriptCommand(BaseCommand):
    """Run a custom script."""

    def execute(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        try:
            if not params or "script_path" not in params:
                raise ValueError("script_path is required")
            
            script_path = params.get("script_path")
            
            if not os.path.exists(script_path):
                raise FileNotFoundError(f"Script not found: {script_path}")
            
            # Execute script
            result_output = subprocess.run(
                ['python', script_path],
                capture_output=True,
                text=True,
                timeout=300  # 5-minute timeout
            )
            
            result = CommandResult(
                success=result_output.returncode == 0,
                result={
                    "stdout": result_output.stdout,
                    "returncode": result_output.returncode
                },
                error=result_output.stderr if result_output.returncode != 0 else None
            )
        except Exception as e:
            result = CommandResult(success=False, error=f"Failed to run script: {str(e)}")
        
        return result.to_dict()


# Command registry
COMMAND_REGISTRY = {
    "open_chrome": OpenChromeCommand(),
    "open_whatsapp": OpenWhatsAppCommand(),
    "shutdown": ShutdownCommand(),
    "restart": RestartCommand(),
    "take_screenshot": TakeScreenshotCommand(),
    "system_info": SystemInfoCommand(),
    "run_script": RunScriptCommand(),
}


def get_command(command_name: str) -> BaseCommand:
    """Get command executor by name."""
    return COMMAND_REGISTRY.get(command_name)


def execute_command(command_name: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
    """Execute a command."""
    command = get_command(command_name)
    if not command:
        return {
            "success": False,
            "error": f"Unknown command: {command_name}"
        }
    
    try:
        logger.info(f"Executing command: {command_name}")
        result = command.execute(params)
        logger.info(f"Command completed: {command_name}")
        return result
    except Exception as e:
        logger.error(f"Command execution error: {str(e)}")
        return {
            "success": False,
            "error": f"Command execution error: {str(e)}"
        }
