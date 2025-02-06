import pathlib
from typing import Optional

class PathValidationError(Exception):
    """Exception raised for path validation errors."""
    pass

class PathHandler:
    """Handles path operations and validation."""
    
    def __init__(self, base_dir: Optional[str] = None):
        """
        Initialize path handler.
        
        Args:
            base_dir: Optional base directory to restrict file operations to
        """
        self.base_dir = pathlib.Path(base_dir).resolve() if base_dir else None
    
    def validate_path(self, file_path: str) -> str:
        """
        Validates and normalizes a file path.
        
        Args:
            file_path: Path to validate
            
        Returns:
            Normalized absolute path
            
        Raises:
            PathValidationError: If path is invalid or outside base directory
        """
        try:
            path = pathlib.Path(file_path).resolve()
            
            # If base_dir is set, ensure path is within it
            if self.base_dir and not str(path).startswith(str(self.base_dir)):
                raise PathValidationError(
                    f"Access denied: Path '{path}' is outside the allowed directory '{self.base_dir}'"
                )
            
            return str(path)
        except Exception as e:
            if isinstance(e, PathValidationError):
                raise
            raise PathValidationError(f"Invalid path '{file_path}': {str(e)}")
    
    def ensure_parent_exists(self, file_path: str) -> None:
        """
        Ensures the parent directory of a file exists.
        
        Args:
            file_path: Path to check
        """
        pathlib.Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    
    def get_size(self, file_path: str) -> int:
        """
        Gets the size of a file.
        
        Args:
            file_path: Path to check
            
        Returns:
            Size in bytes
            
        Raises:
            PathValidationError: If file doesn't exist or is inaccessible
        """
        path = pathlib.Path(self.validate_path(file_path))
        if not path.exists():
            raise PathValidationError(f"File not found: {path}")
        return path.stat().st_size 