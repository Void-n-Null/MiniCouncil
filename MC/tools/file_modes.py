"""File Modes Module - Defines enumerations for file operations.

This module provides:
- Read mode enumeration (READ_ALL, READ_LINES, READ_CHUNKED)
- Write mode enumeration (WRITE, APPEND)
- File mode string conversion
- Mode validation utilities
"""

from enum import Enum, auto

class ReadMode(Enum):
    """Enumeration of file reading modes."""
    READ_ALL = auto()
    READ_LINES = auto()
    READ_CHUNKED = auto()

class WriteMode(Enum):
    """Enumeration of file writing modes."""
    WRITE = auto()
    APPEND = auto()

    @property
    def file_mode(self) -> str:
        """Get the file mode string for open()."""
        return 'a' if self == WriteMode.APPEND else 'w' 