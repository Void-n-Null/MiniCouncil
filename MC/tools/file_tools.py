"""File Tools Module - Tools for file operations.

This module provides tools for:
- Reading files in various modes
- Writing and appending to files
- Checking file existence and size
- File path validation and safety
"""

import logging
import os
from typing import List, Optional, Union
from ..core.base_tool import BaseTool
from ..core.path_handler import PathHandler, PathValidationError
from ..core.encoding import EncodingHandler
from .file_modes import ReadMode, WriteMode

# Configure logger
logger = logging.getLogger(__name__)

class FileToolError(Exception):
    """Base class for file tool exceptions."""

class ReadFileTool(BaseTool):
    """Tool for reading file contents in various modes.
    
    Supports:
    - Reading entire file
    - Reading specific number of bytes
    - Reading lines
    - Reading in chunks
    """
    name = "read_file"
    description = (
        "Reads the contents of a file. Input should be a file path."
    )

    def __init__(
        self,
        chunk_size: int = 4096,
        encoding: str = 'utf-8',
        base_dir: Optional[str] = None
    ):
        """
        Initialize ReadFileTool.
        
        Args:
            chunk_size: Size of chunks when reading in chunked mode
            encoding: Text encoding to use
            base_dir: Optional base directory to restrict file operations to
        """
        self.chunk_size = chunk_size
        self.path_handler = PathHandler(base_dir)
        self.encoding_handler = EncodingHandler(encoding)

    async def _execute(
        self,
        path: str,
        mode: Union[ReadMode, str] = ReadMode.READ_ALL,
        offset: int = 0,
        num_bytes: Optional[int] = None
    ) -> Union[str, List[str]]:
        """
        Reads the file based on the specified mode.
        
        Args:
            path: Path to the file to read
            mode: Reading mode (ReadMode enum or string)
            offset: Starting position for reading
            num_bytes: Number of bytes to read (None for all)
        """
        # Convert string mode to enum if necessary
        if isinstance(mode, str):
            try:
                mode = ReadMode[mode.upper()]
            except KeyError as exc:
                raise FileToolError(f"Invalid read mode: {mode}") from exc

        try:
            file_path = self.path_handler.validate_path(path)
            
            with self.encoding_handler.open_file(file_path, 'r') as f:
                if mode == ReadMode.READ_ALL:
                    f.seek(offset)
                    return f.read(num_bytes) if num_bytes else f.read()
                
                if mode == ReadMode.READ_LINES:
                    return f.readlines()
                
                if mode == ReadMode.READ_CHUNKED:
                    f.seek(offset)
                    chunks = []
                    while True:
                        chunk = f.read(self.chunk_size)
                        if not chunk:
                            break
                        chunks.append(chunk)
                    return ''.join(chunks)
                
                raise FileToolError(f"Unsupported read mode: {mode}")
                    
        except FileNotFoundError as exc:
            logger.error("File not found: %s", path)
            raise FileToolError(f"File not found: {path}") from exc
        except PermissionError as exc:
            logger.error("Permission denied: %s", path)
            raise FileToolError(f"Permission denied: {path}") from exc
        except OSError as exc:
            logger.error("OS error reading file: %s", exc)
            raise FileToolError(f"Error reading file: {exc}") from exc
        except (UnicodeError, LookupError) as exc:
            logger.error("Encoding error reading file: %s", exc)
            raise FileToolError(f"Encoding error reading file: {exc}") from exc
        except Exception as exc:
            logger.error("Unexpected error reading file: %s", exc, exc_info=True)
            raise FileToolError(f"Error reading file: {exc}") from exc


class WriteFileTool(BaseTool):
    """Tool for writing content to files.
    
    Supports:
    - Writing new files
    - Appending to existing files
    - Creating directories if needed
    """
    name = "write_file"
    description = "Writes content to a file. Input should be a file path and content."

    def __init__(self, encoding: str = 'utf-8', base_dir: Optional[str] = None):
        """
        Initialize WriteFileTool.
        
        Args:
            encoding: Text encoding to use
            base_dir: Optional base directory to restrict file operations to
        """
        self.path_handler = PathHandler(base_dir)
        self.encoding_handler = EncodingHandler(encoding)

    async def _execute(
        self,
        path: str,
        content: str,
        mode: Union[WriteMode, str] = WriteMode.WRITE
    ) -> str:
        """
        Writes content to a file.
        
        Args:
            path: Path to the file to write
            content: Content to write to the file
            mode: Writing mode (WriteMode enum or string)
        """
        # Convert string mode to enum if necessary
        if isinstance(mode, str):
            try:
                mode = WriteMode[mode.upper()]
            except KeyError as exc:
                raise FileToolError(f"Invalid write mode: {mode}") from exc

        try:
            file_path = self.path_handler.validate_path(path)
            self.path_handler.ensure_parent_exists(file_path)
            
            with self.encoding_handler.open_file(file_path, mode.file_mode) as f:
                f.write(content)
            return f"Successfully wrote to {file_path} in {mode.name.lower()} mode."
            
        except PathValidationError as exc:
            raise FileToolError(str(exc)) from exc
        except PermissionError as exc:
            logger.error("Permission denied: %s", path)
            raise FileToolError(f"Permission denied: {path}") from exc
        except OSError as exc:
            logger.error("OS error writing to file: %s", exc)
            raise FileToolError(f"Error writing to file: {exc}") from exc
        except Exception as exc:
            logger.error("Error writing to file: %s", exc, exc_info=True)
            raise FileToolError(f"Error writing to file: {exc}") from exc


class FileExistsTool(BaseTool):
    """Tool for checking if a file exists.
    
    Returns True if the file exists and is accessible,
    False otherwise.
    """
    name = "file_exists"
    description = "Checks if a file exists. Input should be a file path."

    def __init__(self, base_dir: Optional[str] = None):
        """
        Initialize FileExistsTool.
        
        Args:
            base_dir: Optional base directory to restrict file operations to
        """
        self.path_handler = PathHandler(base_dir)

    async def _execute(self, path: str) -> bool:
        """
        Checks if a file exists.
        
        Args:
            path: Path to the file to check
            
        Returns:
            True if file exists and is accessible, False otherwise
        """
        try:
            file_path = self.path_handler.validate_path(path)
            return PathHandler().get_size(file_path) >= 0
        except (PathValidationError, FileNotFoundError, PermissionError):
            return False
        except (OSError, IOError) as exc:
            logger.error("Error checking file existence: %s", exc)
            return False


class FileSizeTool(BaseTool):
    """Tool for getting the size of a file in bytes.
    
    Raises FileToolError if the file doesn't exist or
    is not accessible.
    """
    name = "file_size"
    description = "Checks the size of a file in bytes. Input should be a file path."

    def __init__(self, base_dir: Optional[str] = None):
        """
        Initialize FileSizeTool.
        
        Args:
            base_dir: Optional base directory to restrict file operations to
        """
        self.path_handler = PathHandler(base_dir)

    async def _execute(self, path: str) -> int:
        """
        Checks the size of a file.
        
        Args:
            path: Path to the file to check
            
        Returns:
            Size in bytes
            
        Raises:
            FileToolError: If file doesn't exist or is not accessible
        """
        try:
            return self.path_handler.get_size(path)
        except PathValidationError as exc:
            raise FileToolError(str(exc)) from exc
        except FileNotFoundError as exc:
            logger.error("File not found: %s", path)
            raise FileToolError(f"File not found: {path}") from exc
        except PermissionError as exc:
            logger.error("Permission denied: %s", path)
            raise FileToolError(f"Permission denied: {path}") from exc
        except (OSError, IOError) as exc:
            logger.error("Error accessing file: %s", exc)
            raise FileToolError(f"Error accessing file: {exc}") from exc 