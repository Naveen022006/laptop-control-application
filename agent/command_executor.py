"""
Command Executor - Executes commands on the laptop
"""
import subprocess
import platform
import os
import sys
import logging
from typing import Any, Dict, Optional
from datetime import datetime
import psutil
import json

logger = logging.getLogger(__name__)


class CommandExecutor:
    """Executes commands on the laptop"""

    def __init__(self):
        """Initialize executor"""
        self.os_type = platform.system()  # Windows, Linux, Darwin
        self.platform = platform.platform()

    async def execute(self, command_type: str, parameters: Dict[str, Any]) -> Any:
        """Execute a command"""
        logger.info(f"Executing command: {command_type}")

        # Command dispatcher
        if command_type == "open_chrome":
            return await self.open_chrome(parameters)
        elif command_type == "open_whatsapp_web":
            return await self.open_whatsapp_web(parameters)
        elif command_type == "shutdown":
            return await self.shutdown(parameters)
        elif command_type == "restart":
            return await self.restart(parameters)
        elif command_type == "lock_screen":
            return await self.lock_screen(parameters)
        elif command_type == "take_screenshot":
            return await self.take_screenshot(parameters)
        elif command_type == "system_info":
            return await self.system_info(parameters)
        elif command_type == "run_python_script":
            return await self.run_python_script(parameters)
        elif command_type == "system_metrics":
            return await self.get_system_metrics(parameters)
        elif command_type == "open_file":
            return await self.open_file(parameters)
        elif command_type == "get_processes":
            return await self.get_processes(parameters)
        else:
            raise ValueError(f"Unknown command type: {command_type}")

    async def open_chrome(self, parameters: Dict[str, Any]) -> Dict[str, str]:
        """Open Chrome browser"""
        try:
            url = parameters.get("url", "")

            if self.os_type == "Windows":
                if url:
                    subprocess.Popen(["start", "chrome", url], shell=True)
                else:
                    subprocess.Popen(["start", "chrome"], shell=True)

            elif self.os_type == "Darwin":  # macOS
                if url:
                    os.system(f"open -a 'Google Chrome' '{url}'")
                else:
                    os.system("open -a 'Google Chrome'")

            elif self.os_type == "Linux":
                if url:
                    subprocess.Popen(["google-chrome", url])
                else:
                    subprocess.Popen(["google-chrome"])

            return {"status": "Chrome opened successfully"}

        except Exception as e:
            raise Exception(f"Failed to open Chrome: {str(e)}")

    async def open_whatsapp_web(self, parameters: Dict[str, Any]) -> Dict[str, str]:
        """Open WhatsApp Web in browser"""
        try:
            url = "https://web.whatsapp.com"

            if self.os_type == "Windows":
                subprocess.Popen(["start", "chrome", url], shell=True)
            elif self.os_type == "Darwin":
                os.system(f"open -a 'Google Chrome' '{url}'")
            elif self.os_type == "Linux":
                subprocess.Popen(["google-chrome", url])

            return {"status": "WhatsApp Web opened successfully"}

        except Exception as e:
            raise Exception(f"Failed to open WhatsApp Web: {str(e)}")

    async def shutdown(self, parameters: Dict[str, Any]) -> Dict[str, str]:
        """Shutdown the laptop"""
        try:
            delay = parameters.get("delay", 0)

            if self.os_type == "Windows":
                subprocess.run(["shutdown", "/s", "/t", str(delay)])
            elif self.os_type == "Darwin":
                subprocess.run(["sudo", "shutdown", "-h", "now"])
            elif self.os_type == "Linux":
                subprocess.run(["sudo", "shutdown", "-h", "now"])

            return {"status": "Shutdown command sent"}

        except Exception as e:
            raise Exception(f"Failed to shutdown: {str(e)}")

    async def restart(self, parameters: Dict[str, Any]) -> Dict[str, str]:
        """Restart the laptop"""
        try:
            delay = parameters.get("delay", 0)

            if self.os_type == "Windows":
                subprocess.run(["shutdown", "/r", "/t", str(delay)])
            elif self.os_type == "Darwin":
                subprocess.run(["sudo", "shutdown", "-r", "now"])
            elif self.os_type == "Linux":
                subprocess.run(["sudo", "shutdown", "-r", "now"])

            return {"status": "Restart command sent"}

        except Exception as e:
            raise Exception(f"Failed to restart: {str(e)}")

    async def lock_screen(self, parameters: Dict[str, Any]) -> Dict[str, str]:
        """Lock the screen"""
        try:
            if self.os_type == "Windows":
                subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
            elif self.os_type == "Darwin":
                subprocess.run(["/System/Library/CoreServices/Menu\\ Extras/User.menu/Contents/Resources/CGSession", "-suspend"])
            elif self.os_type == "Linux":
                subprocess.run(["gnome-screensaver-command", "-l"])

            return {"status": "Screen locked"}

        except Exception as e:
            raise Exception(f"Failed to lock screen: {str(e)}")

    async def take_screenshot(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Take a screenshot"""
        try:
            from PIL import ImageGrab
            import base64
            from io import BytesIO

            # Take screenshot
            screenshot = ImageGrab.grab()

            # Convert to base64
            buffer = BytesIO()
            screenshot.save(buffer, format="PNG")
            img_str = base64.b64encode(buffer.getvalue()).decode()

            return {
                "status": "success",
                "image": img_str,
                "format": "png",
                "size": screenshot.size
            }

        except Exception as e:
            raise Exception(f"Failed to take screenshot: {str(e)}")

    async def system_info(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get system information"""
        try:
            import socket

            return {
                "os": self.os_type,
                "platform": self.platform,
                "processor": platform.processor(),
                "cpu_count": psutil.cpu_count(),
                "total_memory": psutil.virtual_memory().total,
                "hostname": socket.gethostname(),
                "python_version": platform.python_version()
            }

        except Exception as e:
            raise Exception(f"Failed to get system info: {str(e)}")

    async def get_system_metrics(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get system metrics"""
        try:
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            return {
                "cpu_usage": psutil.cpu_percent(interval=1),
                "memory_usage": memory.percent,
                "memory_available": memory.available,
                "disk_usage": disk.percent,
                "disk_free": disk.free,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            raise Exception(f"Failed to get metrics: {str(e)}")

    async def run_python_script(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a Python script"""
        try:
            script_code = parameters.get("code", "")
            timeout = parameters.get("timeout", 30)

            if not script_code:
                raise ValueError("No code provided")

            # Execute in subprocess for safety
            result = subprocess.run(
                [sys.executable, "-c", script_code],
                capture_output=True,
                text=True,
                timeout=timeout
            )

            return {
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }

        except subprocess.TimeoutExpired:
            raise Exception("Script execution timed out")
        except Exception as e:
            raise Exception(f"Failed to execute script: {str(e)}")

    async def open_file(self, parameters: Dict[str, Any]) -> Dict[str, str]:
        """Open a file"""
        try:
            file_path = parameters.get("path", "")

            if not file_path or not os.path.exists(file_path):
                raise ValueError(f"File not found: {file_path}")

            if self.os_type == "Windows":
                os.startfile(file_path)
            elif self.os_type == "Darwin":
                subprocess.run(["open", file_path])
            elif self.os_type == "Linux":
                subprocess.run(["xdg-open", file_path])

            return {"status": f"File opened: {file_path}"}

        except Exception as e:
            raise Exception(f"Failed to open file: {str(e)}")

    async def get_processes(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Get list of running processes"""
        try:
            processes = []

            for proc in psutil.process_iter(["pid", "name", "status"]):
                try:
                    processes.append({
                        "pid": proc.pid,
                        "name": proc.name(),
                        "status": proc.status()
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            return {
                "process_count": len(processes),
                "processes": processes[:50]  # Return first 50
            }

        except Exception as e:
            raise Exception(f"Failed to get processes: {str(e)}")

    def get_system_info(self) -> Dict[str, Any]:
        """Get system information for status updates"""
        try:
            import socket

            return {
                "os": self.os_type,
                "platform": self.platform,
                "processor": platform.processor(),
                "cpu_count": psutil.cpu_count(),
                "hostname": socket.gethostname(),
                "cpu_usage": psutil.cpu_percent(interval=1),
                "memory_usage": psutil.virtual_memory().percent
            }

        except Exception as e:
            logger.error(f"Error getting system info: {str(e)}")
            return {}
