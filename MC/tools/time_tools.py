from datetime import datetime
from typing import Optional
from .base import BaseTool

class GetTimeTool(BaseTool):
    """Get the current time."""
    name = "get_current_time"
    description = "Get the current time in the specified format"
    
    async def execute(self, format: str = "%Y-%m-%d %H:%M:%S") -> str:
        """
        Get the current time in the specified format.
        
        Args:
            format: Optional datetime format string (default: "%Y-%m-%d %H:%M:%S")
        """
        try:
            return datetime.now().strftime(format)
        except Exception as e:
            return f"Error getting time: {str(e)}" 