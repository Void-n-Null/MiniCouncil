import pytest
from pathlib import Path
from MC.tools.file_tools import (
    ReadFileTool, WriteFileTool, FileExistsTool, FileSizeTool,
    FileToolError
)
from MC.tools.file_modes import ReadMode, WriteMode
from MC.tools.path_handler import PathValidationError

@pytest.fixture
def temp_file(tmp_path):
    file_path = tmp_path / "test.txt"
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("test content\nline 2")
    return file_path

@pytest.fixture
def read_tool():
    return ReadFileTool()

@pytest.fixture
def write_tool():
    return WriteFileTool()

@pytest.fixture
def exists_tool():
    return FileExistsTool()

@pytest.fixture
def size_tool():
    return FileSizeTool()

# ReadFileTool Tests
@pytest.mark.asyncio
async def test_read_file_all(read_tool, temp_file):
    content = await read_tool._execute(str(temp_file), ReadMode.READ_ALL)
    assert content == "test content\nline 2"

@pytest.mark.asyncio
async def test_read_file_lines(read_tool, temp_file):
    lines = await read_tool._execute(str(temp_file), ReadMode.READ_LINES)
    assert lines == ["test content\n", "line 2"]

@pytest.mark.asyncio
async def test_read_file_chunked(read_tool, temp_file):
    content = await read_tool._execute(str(temp_file), ReadMode.READ_CHUNKED)
    assert content == "test content\nline 2"

@pytest.mark.asyncio
async def test_read_file_with_offset(read_tool, temp_file):
    content = await read_tool._execute(str(temp_file), ReadMode.READ_ALL, offset=5)
    assert content == "content\nline 2"

@pytest.mark.asyncio
async def test_read_file_with_num_bytes(read_tool, temp_file):
    content = await read_tool._execute(str(temp_file), ReadMode.READ_ALL, num_bytes=4)
    assert content == "test"

@pytest.mark.asyncio
async def test_read_nonexistent_file(read_tool):
    with pytest.raises(FileToolError) as exc_info:
        await read_tool._execute("nonexistent.txt")
    assert "No such file or directory" in str(exc_info.value)

@pytest.mark.asyncio
async def test_read_invalid_mode(read_tool, temp_file):
    with pytest.raises(FileToolError) as exc_info:
        await read_tool._execute(str(temp_file), "invalid_mode")
    assert "Invalid read mode" in str(exc_info.value)

# WriteFileTool Tests
@pytest.mark.asyncio
async def test_write_file(write_tool, tmp_path):
    file_path = tmp_path / "write_test.txt"
    content = "new content"
    result = await write_tool._execute(str(file_path), content, WriteMode.WRITE)
    assert "Successfully wrote" in result
    assert file_path.read_text(encoding="utf-8") == content

@pytest.mark.asyncio
async def test_append_file(write_tool, temp_file):
    content = "\nappended content"
    result = await write_tool._execute(str(temp_file), content, WriteMode.APPEND)
    assert "Successfully wrote" in result
    assert "appended content" in Path(temp_file).read_text(encoding="utf-8")

@pytest.mark.asyncio
async def test_write_invalid_path(write_tool):
    with pytest.raises(FileToolError) as exc_info:
        await write_tool._execute("/invalid/path/file.txt", "content")
    assert "Permission denied" in str(exc_info.value)

@pytest.mark.asyncio
async def test_write_invalid_mode(write_tool, temp_file):
    with pytest.raises(FileToolError) as exc_info:
        await write_tool._execute(str(temp_file), "content", "invalid_mode")
    assert "Invalid write mode" in str(exc_info.value)

# FileExistsTool Tests
@pytest.mark.asyncio
async def test_file_exists(exists_tool, temp_file):
    result = await exists_tool._execute(str(temp_file))
    assert result is True

@pytest.mark.asyncio
async def test_file_does_not_exist(exists_tool, tmp_path):
    result = await exists_tool._execute(str(tmp_path / "nonexistent.txt"))
    assert result is False

# FileSizeTool Tests
@pytest.mark.asyncio
async def test_file_size(size_tool, temp_file):
    size = await size_tool._execute(str(temp_file))
    assert size == len("test content\nline 2")

@pytest.mark.asyncio
async def test_file_size_nonexistent(size_tool):
    with pytest.raises(FileToolError) as exc_info:
        await size_tool._execute("nonexistent.txt")
    assert "File not found" in str(exc_info.value)

# Base Directory Tests
@pytest.mark.asyncio
async def test_base_dir_restriction():
    base_dir = "/tmp/restricted"
    read_tool = ReadFileTool(base_dir=base_dir)
    with pytest.raises(FileToolError) as exc_info:
        await read_tool._execute("/etc/passwd")
    assert "outside the allowed directory" in str(exc_info.value)

# Encoding Tests
@pytest.mark.asyncio
async def test_custom_encoding():
    read_tool = ReadFileTool(encoding="latin1")
    write_tool = WriteFileTool(encoding="latin1")
    content = "áéíóú"
    
    # Write with latin1 encoding
    file_path = Path("/tmp/encoding_test.txt")
    await write_tool._execute(str(file_path), content)
    
    # Read with latin1 encoding
    result = await read_tool._execute(str(file_path))
    assert result == content 