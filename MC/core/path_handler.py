"""Path Handler Module - Manages file path operations safely.

This module provides:
- File path validation
- Path safety checks
- Directory creation and management
- Path resolution and normalization
- Base directory restrictions
"""

import os
from pathlib import Path
from typing import Optional

class PathValidationError(Exception):
    """Exception raised when a path fails validation."""

class PathHandler:
    """Handles file path operations safely."""
    
    def __init__(self, base_dir: Optional[str] = None):
        """
        Initialize PathHandler.
        
        Args:
            base_dir: Optional base directory to restrict operations to
        """
        self.base_dir = Path(base_dir).resolve() if base_dir else None
    
    def validate_path(self, file_path: str) -> Path:
        """
        Validate and resolve a file path.
        
        Args:
            file_path: Path to validate
            
        Returns:
            Resolved Path object
            
        Raises:
            PathValidationError: If path is invalid or outside base directory
        """
        try:
            path = Path(file_path).resolve()
            
            if self.base_dir and not str(path).startswith(str(self.base_dir)):
                raise PathValidationError(
                    f"Path '{file_path}' is outside the allowed directory"
                )
            
            return path
            
        except Exception as exc:
            raise PathValidationError(
                f"Invalid path '{file_path}': {str(exc)}"
            ) from exc
    
    def ensure_parent_exists(self, file_path: Path) -> None:
        """
        Ensure the parent directory of a file exists.
        
        Args:
            file_path: Path to check
            
        Raises:
            PathValidationError: If directory creation fails
        """
        parent = file_path.parent
        parent.mkdir(parents=True, exist_ok=True)
    
    def get_size(self, file_path: str) -> int:
        """
        Get the size of a file in bytes.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Size in bytes
            
        Raises:
            PathValidationError: If path is invalid
            FileNotFoundError: If file doesn't exist
        """
        path = Path(file_path).resolve()
        return path.stat().st_size 