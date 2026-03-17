"""
Helper functions for common operations.
"""
import json
from typing import Dict, Any
from datetime import datetime


def convert_dict_to_json(data: Dict[str, Any]) -> str:
    """Convert dictionary to JSON string."""
    try:
        return json.dumps(data)
    except (TypeError, ValueError) as e:
        return json.dumps({"error": str(e)})


def convert_json_to_dict(json_str: str) -> Dict[str, Any]:
    """Convert JSON string to dictionary."""
    try:
        return json.loads(json_str) if json_str else {}
    except (json.JSONDecodeError, ValueError):
        return {}


def get_timestamp() -> str:
    """Get current timestamp as ISO format."""
    return datetime.utcnow().isoformat()


def calculate_execution_time(start_time: datetime, end_time: datetime) -> int:
    """Calculate execution time in milliseconds."""
    return int((end_time - start_time).total_seconds() * 1000)
