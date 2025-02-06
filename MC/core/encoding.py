"""Encoding Module - Handles text encoding operations.

This module provides:
- Text encoding/decoding utilities
- File encoding management
- Encoding validation
- Default encoding configuration
- Encoding error handling
"""

from typing import Optional

class EncodingHandler:
    """Handles text encoding operations."""
    
    def __init__(self, encoding: str = 'utf-8', errors: str = 'strict'):
        """
        Initialize encoding handler.
        
        Args:
            encoding: Text encoding to use
            errors: How to handle encoding errors
        """
        self.encoding = encoding
        self.errors = errors
    
    def open_file(self, path: str, mode: str):
        """
        Open a file with proper encoding.
        
        Args:
            path: Path to the file
            mode: File mode ('r' or 'w')
            
        Returns:
            File object
        """
        return open(path, mode=mode, encoding=self.encoding, errors=self.errors) 