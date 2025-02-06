"""Tests for the tool implementations."""

import pytest
import os
from datetime import datetime
from MC.tools.file_tools import ReadFileTool, WriteFileTool, FileExistsTool, FileSizeTool, FileToolError
from MC.tools.time_tools import GetTimeTool
from MC.tools.file_modes import ReadMode, WriteMode

@pytest.mark.asyncio
async def test_read_file_tool(tmp_path):
    """Test the ReadFileTool."""
    tool = ReadFileTool()
    test_file = tmp_path / "test.txt"
    
    # Test reading non-existent file
    with pytest.raises(FileToolError) as exc_info:
        await tool.execute(path=str(test_file))
    assert "File not found" in str(exc_info.value)
    
    # Test reading existing file
    test_content = "Hello, World!"
    with open(test_file, "w", encoding='utf-8') as f:
        f.write(test_content)
    
    try:
        # Test default read mode
        result = await tool.execute(path=str(test_file))
        assert result == test_content
        
        # Test read_lines mode
        result = await tool.execute(path=str(test_file), mode=ReadMode.READ_LINES)
        assert result == [test_content]
        
        # Test read_chunked mode
        result = await tool.execute(path=str(test_file), mode=ReadMode.READ_CHUNKED)
        assert result == test_content
        
        # Test invalid mode
        with pytest.raises(FileToolError) as exc_info:
            await tool.execute(path=str(test_file), mode="invalid_mode")
        assert "Invalid read mode" in str(exc_info.value)
        
    finally:
        # Clean up
        test_file.unlink(missing_ok=True)

@pytest.mark.asyncio
async def test_write_file_tool(tmp_path):
    """Test the WriteFileTool."""
    tool = WriteFileTool()
    test_file = tmp_path / "test.txt"
    test_content = "Test content"
    
    try:
        # Test writing to file
        result = await tool.execute(path=str(test_file), content=test_content)
        assert "Successfully" in result
        
        # Verify file contents
        with open(test_file, "r", encoding='utf-8') as f:
            assert f.read() == test_content
        
        # Test append mode
        append_content = "\nMore content"
        result = await tool.execute(
            path=str(test_file),
            content=append_content,
            mode=WriteMode.APPEND
        )
        assert "Successfully" in result
        assert "append" in result.lower()
        
        # Verify appended content
        with open(test_file, "r", encoding='utf-8') as f:
            content = f.read()
            assert content == test_content + append_content
        
        # Test creating directories
        nested_file = tmp_path / "test_dir" / "nested" / "file.txt"
        result = await tool.execute(path=str(nested_file), content=test_content)
        assert "Successfully" in result
        assert nested_file.exists()
        
    finally:
        # Clean up
        test_file.unlink(missing_ok=True)
        if nested_file.exists():
            nested_file.unlink()

@pytest.mark.asyncio
async def test_file_exists_tool(tmp_path):
    """Test the FileExistsTool."""
    tool = FileExistsTool()
    test_file = tmp_path / "test.txt"
    
    # Test non-existent file
    result = await tool.execute(path=str(test_file))
    assert result is False
    
    # Create file and test again
    test_file.write_text("test", encoding='utf-8')
    
    try:
        result = await tool.execute(path=str(test_file))
        assert result is True
    finally:
        test_file.unlink(missing_ok=True)

@pytest.mark.asyncio
async def test_file_size_tool(tmp_path):
    """Test the FileSizeTool."""
    tool = FileSizeTool()
    test_file = tmp_path / "test.txt"
    test_content = "Hello, World!"
    
    # Test non-existent file
    with pytest.raises(FileToolError) as exc_info:
        await tool.execute(path=str(test_file))
    assert "File not found" in str(exc_info.value)
    
    # Create file and test size
    test_file.write_text(test_content, encoding='utf-8')
    
    try:
        result = await tool.execute(path=str(test_file))
        assert result == len(test_content)
    finally:
        test_file.unlink(missing_ok=True)

@pytest.mark.asyncio
async def test_get_time_tool():
    """Test the GetTimeTool."""
    tool = GetTimeTool()
    
    # Test default format
    result = await tool.execute()
    # Verify result can be parsed as datetime
    try:
        datetime.strptime(result, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        pytest.fail("Time string not in expected format")
    
    # Test custom format
    custom_format = "%Y-%m-%d"
    result = await tool.execute(format=custom_format)
    try:
        datetime.strptime(result, custom_format)
    except ValueError:
        pytest.fail("Time string not in custom format")
    
    # Test invalid format
    result = await tool.execute(format="%Y-%m-%d %H:%M:%S %Q")  # %Q is not valid
    assert "Error: Invalid datetime format" in result

def test_tool_schemas():
    """Test that all tools have valid schemas."""
    tools = [ReadFileTool, WriteFileTool, FileExistsTool, FileSizeTool]
    
    for tool_class in tools:
        schema = tool_class.get_tool_schema()
        
        # Check basic schema structure
        assert schema["type"] == "function"
        assert "function" in schema
        assert "name" in schema["function"]
        assert "description" in schema["function"]
        assert "parameters" in schema["function"]
        
        # Check that name and description are not empty
        assert schema["function"]["name"]
        assert schema["function"]["description"]
        
        # Check parameters schema
        params = schema["function"]["parameters"]
        assert params["type"] == "object"
        assert "properties" in params
        
        # Specific checks for each tool
        if tool_class == ReadFileTool:
            assert "path" in params["properties"]
            assert "mode" in params["properties"]
            assert "offset" in params["properties"]
            assert "num_bytes" in params["properties"]
            
        elif tool_class == WriteFileTool:
            assert "path" in params["properties"]
            assert "content" in params["properties"]
            assert "mode" in params["properties"]
            
        elif tool_class == FileExistsTool:
            assert "path" in params["properties"]
            
        elif tool_class == FileSizeTool:
            assert "path" in params["properties"] 