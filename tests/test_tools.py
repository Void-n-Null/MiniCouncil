import pytest
import os
from datetime import datetime
from MC.tools.file_tools import ReadFileTool, WriteFileTool
from MC.tools.time_tools import GetTimeTool

@pytest.mark.asyncio
async def test_read_file_tool():
    """Test the ReadFileTool."""
    tool = ReadFileTool()
    
    # Test reading non-existent file
    result = await tool.execute(path="non_existent_file.txt")
    assert "Error" in result
    
    # Test reading existing file
    test_content = "Hello, World!"
    with open("test_file.txt", "w") as f:
        f.write(test_content)
    
    try:
        result = await tool.execute(path="test_file.txt")
        assert result == test_content
    finally:
        # Clean up
        os.remove("test_file.txt")

@pytest.mark.asyncio
async def test_write_file_tool():
    """Test the WriteFileTool."""
    tool = WriteFileTool()
    test_content = "Test content"
    test_file = "test_output.txt"
    
    try:
        # Test writing to file
        result = await tool.execute(path=test_file, content=test_content)
        assert "Successfully" in result
        
        # Verify file contents
        with open(test_file, "r") as f:
            assert f.read() == test_content
            
        # Test writing to invalid path
        result = await tool.execute(path="/invalid/path/file.txt", content="test")
        assert "Error" in result
    finally:
        # Clean up
        if os.path.exists(test_file):
            os.remove(test_file)

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
    
    # Test invalid format - use a format string that will definitely fail
    result = await tool.execute(format="%Y-%m-%d %H:%M:%S %Q")  # %Q is not a valid directive
    assert "Error: Invalid datetime format" in result

def test_tool_schemas():
    """Test that all tools have valid schemas."""
    tools = [ReadFileTool, WriteFileTool, GetTimeTool]
    
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
            assert params["properties"]["path"]["type"] == "string"
            
        elif tool_class == WriteFileTool:
            assert "path" in params["properties"]
            assert "content" in params["properties"]
            assert params["properties"]["path"]["type"] == "string"
            assert params["properties"]["content"]["type"] == "string"
            
        elif tool_class == GetTimeTool:
            assert "format" in params["properties"]
            assert params["properties"]["format"]["type"] == "string"
            # Check that format is optional
            assert "format" not in params.get("required", []) 