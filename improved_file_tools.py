import os
import pathlib
import logging

# Configure logging (can be further customized)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FileToolError(Exception):
    """Base class for file tool exceptions."""
    pass


class BaseFileTool:
    def __init__(self, encoding='utf-8'):
        self.encoding = encoding

    def _sanitize_path(self, file_path):
        """Sanitizes the file path to prevent path traversal attacks."""
        try:
            # Resolve the path to its absolute form and normalize it.
            abs_path = pathlib.Path(file_path).resolve().as_posix()

            # Check if the resolved path starts with the intended base directory.
            # This prevents access to files outside the allowed directories.
            # For example, if you want to restrict access to a specific directory:
            # if not abs_path.startswith("/path/to/allowed/directory"):
            #     raise FileToolError("Access denied: Path is outside the allowed directory.")

            return abs_path
        except Exception as e:
            raise FileToolError(f"Invalid file path: {e}") from e


class ReadFileTool(BaseFileTool):
    def __init__(self, encoding='utf-8', chunk_size=4096):
        super().__init__(encoding)
        self.name = "Read File"
        self.description = "Reads the contents of a file. Input should be a file path."
        self.chunk_size = chunk_size

    def use(self, file_path, mode='read_all', offset=0, num_bytes=None):
        """Reads the file based on the specified mode."""
        file_path = self._sanitize_path(file_path)
        try:
            with open(file_path, 'r', encoding=self.encoding) as f:
                if mode == 'read_all':
                    f.seek(offset)
                    if num_bytes is None:
                        content = f.read()
                    else:
                        content = f.read(num_bytes)
                    return content
                elif mode == 'read_lines':
                    return f.readlines()
                elif mode == 'read_chunked':
                    f.seek(offset)
                    def chunk_generator():
                        while True:
                            chunk = f.read(self.chunk_size)
                            if not chunk:
                                break
                            yield chunk
                    return chunk_generator() # Returns a generator
                else:
                    raise FileToolError("Invalid read mode.")
        except FileNotFoundError:
            raise FileToolError(f"File not found at path: {file_path}")
        except PermissionError:
            raise FileToolError(f"Permission denied for file: {file_path}")
        except Exception as e:
            logging.error(f"Error reading file: {e}", exc_info=True)
            raise FileToolError(f"Error reading file: {e}") from e


class WriteFileTool(BaseFileTool):
    def __init__(self, encoding='utf-8'):
        super().__init__(encoding)
        self.name = "Write File"
        self.description = "Writes content to a file. Input should be a file path and the content to write, separated by a delimiter (e.g., 'path|content')."

    def use(self, file_path_and_content, mode='write'):
        """Writes content to a file."""
        try:
            file_path, content = file_path_and_content.split('|', 1)
            file_path = self._sanitize_path(file_path)

            # Create directories if they don't exist
            pathlib.Path(file_path).parent.mkdir(parents=True, exist_ok=True)

            open_mode = 'w' if mode == 'write' else 'a'  # 'a' for append
            with open(file_path, open_mode, encoding=self.encoding) as f:
                f.write(content)
            return f"Successfully wrote to {file_path} in {mode} mode."

        except ValueError:
            raise FileToolError("Input should be 'file_path|content'.")
        except PermissionError:
            raise FileToolError(f"Permission denied for file: {file_path}")
        except OSError as e:
            raise FileToolError(f"OS error writing to file: {e}")
        except Exception as e:
            logging.error(f"Error writing to file: {e}", exc_info=True)
            raise FileToolError(f"Error writing to file: {e}") from e

class FileExistsTool:
    def __init__(self):
        self.name = "File Exists"
        self.description = "Checks if a file exists. Input should be a file path."

    def use(self, file_path):
        """Checks if a file exists."""
        try:
            file_path = pathlib.Path(file_path)
            return file_path.exists()
        except Exception as e:
            logging.error(f"Error checking file existence: {e}", exc_info=True)
            return False

class FileSizeTool:
    def __init__(self):
        self.name = "File Size"
        self.description = "Checks the size of a file in bytes. Input should be a file path."

    def use(self, file_path):
        """Checks the size of a file."""
        try:
            file_path = pathlib.Path(file_path)
            if not file_path.exists():
                raise FileToolError(f"File not found: {file_path}")

            return file_path.stat().st_size
        except FileToolError as e:
            raise e # Re-raise FileToolError
        except Exception as e:
            logging.error(f"Error checking file size: {e}", exc_info=True)
            raise FileToolError(f"Error checking file size: {e}") from e


if __name__ == '__main__':
    # Example Usage (Demonstrates improved error handling and features)
    try:
        # Read a file
        reader = ReadFileTool()
        content = reader.use("example.txt")
        print(f"File content:\n{content}")

        # Read lines
        reader = ReadFileTool()
        lines = reader.use("example.txt", mode='read_lines')
        print(f"Lines in file:\n{lines}")

        # Read chunked
        reader = ReadFileTool()
        chunk_generator = reader.use("example.txt", mode='read_chunked')
        print("Chunked reading:")
        for chunk in chunk_generator:
            print(chunk)

        # Write to a file
        writer = WriteFileTool()
        result = writer.use("output_directory/output.txt|This is some content to write.")
        print(result)

        # Append to a file
        result = writer.use("output_directory/output.txt|This is some content to append.", mode='append')
        print(result)

        # Check if a file exists
        exists_tool = FileExistsTool()
        exists = exists_tool.use("output_directory/output.txt")
        print(f"File exists: {exists}")

        # Get file size
        size_tool = FileSizeTool()
        size = size_tool.use("output_directory/output.txt")
        print(f"File size: {size} bytes")

        # Demonstrate error handling
        reader = ReadFileTool()
        reader.use("non_existent_file.txt")

    except FileToolError as e:
        print(f"An error occurred: {e}")
    except Exception as e:
        print(f"A unexpected error occurred: {e}") 