"""Time Tools Module - Tools for time-related operations.

This module provides tools for:
- Getting the current time in various formats
- Time formatting and validation
- Time-related utility functions
"""

from datetime import datetime
from typing import Optional
from ..core.base_tool import BaseTool

class TimeToolError(Exception):
    """Base class for time tool exceptions."""

class GetTimeTool(BaseTool):
    """Get the current time."""
    name = "get_current_time"
    description = "Get the current time in the specified format"
    
    # Valid format directives in Python's strftime
    VALID_DIRECTIVES = {
        '%a', '%A', '%w', '%d', '%b', '%B', '%m', '%y', '%Y',
        '%H', '%I', '%p', '%M', '%S', '%f', '%z', '%Z',
        '%j', '%U', '%W', '%c', '%x', '%X', '%%'
    }
    
    def _validate_format(self, time_format: str) -> bool:
        """
        Validate that the format string only uses known directives.
        
        Args:
            time_format: The format string to validate
            
        Returns:
            True if format is valid, False otherwise
        """
        i = 0
        while i < len(time_format):
            if time_format[i] == '%':
                if i + 1 >= len(time_format):
                    return False  # Incomplete format directive
                directive = time_format[i:i+2]
                if directive not in self.VALID_DIRECTIVES:
                    return False  # Invalid directive
                i += 2
            else:
                i += 1
        return True
    
    async def _execute(self, time_format: str = "%Y-%m-%d %H:%M:%S") -> str:
        """
        Get the current time in the specified format.
        
        Args:
            time_format: Optional datetime format string (default: "%Y-%m-%d %H:%M:%S")
            
        Returns:
            Formatted time string
            
        Raises:
            TimeToolError: If format string is invalid
        """
        try:
            # First validate the format string
            if not self._validate_format(time_format):
                raise TimeToolError(
                    "Invalid datetime format - contains invalid directives"
                )
            
            # If validation passes, format the time
            now = datetime.now()
            return now.strftime(time_format)
            
        except ValueError as exc:
            raise TimeToolError(f"Invalid datetime format: {str(exc)}") from exc
        except TimeToolError as exc:
            raise exc
        except Exception as exc:
            raise TimeToolError(f"Unexpected error: {str(exc)}") from exc 