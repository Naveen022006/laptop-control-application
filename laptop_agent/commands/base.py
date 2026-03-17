"""
Base command executor interface.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseCommand(ABC):
    """Base class for all executable commands."""

    @abstractmethod
    def execute(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute the command.
        
        Args:
            params: Command parameters
            
        Returns:
            Dictionary with execution result
        """
        pass

    def get_command_name(self) -> str:
        """Get command name."""
        return self.__class__.__name__


class CommandResult:
    """Standard command result format."""

    def __init__(self, success: bool, result: Any = None, error: str = None):
        self.success = success
        self.result = result
        self.error = error

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "result": self.result,
            "error": self.error
        }
