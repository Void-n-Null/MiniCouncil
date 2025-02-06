import logging
from typing import List, Optional, Union
from ..core.base_tool import BaseTool
from ..core.path_handler import PathHandler, PathValidationError
from ..core.encoding import EncodingHandler
from .file_modes import ReadMode, WriteMode

# Note: Logging should be configured by the application, not here
logger = logging.getLogger(__name__)

class FileToolError(Exception):
    """Base class for file tool exceptions."""
    pass

class ReadFileTool(BaseTool):
    name = "read_file"
    description = "Reads the contents of a file. Input should be a file path."

    def __init__(self, chunk_size: int = 4096, encoding: str = 'utf-8', base_dir: Optional[str] = None):
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
            except KeyError:
                raise FileToolError(f"Invalid read mode: {mode}")

        try:
            file_path = self.path_handler.validate_path(path)
            
            with self.encoding_handler.open_file(file_path, 'r') as f:
                if mode == ReadMode.READ_ALL:
                    f.seek(offset)
                    return f.read(num_bytes) if num_bytes else f.read()
                    
                elif mode == ReadMode.READ_LINES:
                    return f.readlines()
                    
                elif mode == ReadMode.READ_CHUNKED:
                    f.seek(offset)
                    chunks = []
                    while True:
                        chunk = f.read(self.chunk_size)
                        if not chunk:
                            break
                        chunks.append(chunk)
                    return ''.join(chunks)
                    
                else:
                    raise FileToolError(f"Unsupported read mode: {mode}")
                    
        except PathValidationError as e:
            raise FileToolError(str(e))
        except Exception as e:
            logger.error(f"Error reading file: {e}", exc_info=True)
            raise FileToolError(f"Error reading file: {e}") from e


class WriteFileTool(BaseTool):
    name = "write_file"
    description = "Writes content to a file. Input should be a file path and the content to write."

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
            except KeyError:
                raise FileToolError(f"Invalid write mode: {mode}")

        try:
            file_path = self.path_handler.validate_path(path)
            self.path_handler.ensure_parent_exists(file_path)
            
            with self.encoding_handler.open_file(file_path, mode.file_mode) as f:
                f.write(content)
            return f"Successfully wrote to {file_path} in {mode.name.lower()} mode."
            
        except PathValidationError as e:
            raise FileToolError(str(e))
        except Exception as e:
            logger.error(f"Error writing to file: {e}", exc_info=True)
            raise FileToolError(f"Error writing to file: {e}") from e


class FileExistsTool(BaseTool):
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
        """
        try:
            file_path = self.path_handler.validate_path(path)
            return PathHandler().get_size(file_path) >= 0
        except Exception as e:
            logger.error(f"Error checking file existence: {e}", exc_info=True)
            return False


class FileSizeTool(BaseTool):
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
        """
        try:
            return self.path_handler.get_size(path)
        except PathValidationError as e:
            raise FileToolError(str(e))
        except Exception as e:
            logger.error(f"Error checking file size: {e}", exc_info=True)
            raise FileToolError(f"Error checking file size: {e}") from e 