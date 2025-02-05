from datetime import datetime
from typing import Optional
from .base import BaseTool

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
    
    def _validate_format(self, format_str: str) -> bool:
        """Validate that the format string only uses known directives."""
        i = 0
        while i < len(format_str):
            if format_str[i] == '%':
                if i + 1 >= len(format_str):
                    return False  # Incomplete format directive
                directive = format_str[i:i+2]
                if directive not in self.VALID_DIRECTIVES:
                    return False  # Invalid directive
                i += 2
            else:
                i += 1
        return True
    
    async def _execute(self, format: str = "%Y-%m-%d %H:%M:%S") -> str:
        """
        Get the current time in the specified format.
        
        Args:
            format: Optional datetime format string (default: "%Y-%m-%d %H:%M:%S")
        """
        try:
            # First validate the format string
            if not self._validate_format(format):
                return "Error: Invalid datetime format - contains invalid directives"
            
            # If validation passes, format the time
            now = datetime.now()
            return now.strftime(format)
        except Exception as e:
            return f"Error: {str(e)}" 