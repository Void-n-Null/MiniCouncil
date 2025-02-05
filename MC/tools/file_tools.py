from typing import Optional
from .base import BaseTool

class ReadFileTool(BaseTool):
    """Read contents of a file."""
    name = "read_file"
    description = "Read the contents of a file at the specified path"
    
    async def execute(self, path: str) -> str:
        """
        Read and return the contents of a file.
        
        Args:
            path: Path to the file to read
        """
        try:
            with open(path, 'r') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"

class WriteFileTool(BaseTool):
    """Write content to a file."""
    name = "write_file"
    description = "Write content to a file at the specified path"
    
    async def execute(self, path: str, content: str) -> str:
        """
        Write content to a file.
        
        Args:
            path: Path to the file to write
            content: Content to write to the file
        """
        try:
            with open(path, 'w') as f:
                f.write(content)
            return f"Successfully wrote to {path}"
        except Exception as e:
            return f"Error writing to file: {str(e)}" 