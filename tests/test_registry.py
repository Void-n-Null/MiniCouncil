import pytest
import os
from typing import Optional
from MC.tools.base import BaseTool
from MC.tools.registry import ToolRegistry

# Example tools for testing
class TestTool1(BaseTool):
    name = "test_tool_1"
    description = "First test tool"
    
    async def execute(self, value: str) -> str:
        return value

class TestTool2(BaseTool):
    name = "test_tool_2"
    description = "Second test tool"
    
    async def execute(self, value: int) -> int:
        return value * 2

def test_registry_initialization():
    """Test that registry initializes properly."""
    registry = ToolRegistry()
    assert len(registry._tools) == 0

def test_tool_registration():
    """Test that tools can be registered."""
    registry = ToolRegistry()
    
    # Register a tool
    registry.register(TestTool1)
    assert len(registry._tools) == 1
    assert "test_tool_1" in registry._tools
    
    # Register another tool
    registry.register(TestTool2)
    assert len(registry._tools) == 2
    assert "test_tool_2" in registry._tools

def test_duplicate_tool_registration():
    """Test that registering a tool with the same name updates the registry."""
    registry = ToolRegistry()
    
    class Tool1(BaseTool):
        name = "same_name"
        async def execute(self, value: str) -> str:
            return value
    
    class Tool2(BaseTool):
        name = "same_name"
        async def execute(self, value: int) -> int:
            return value
    
    registry.register(Tool1)
    registry.register(Tool2)
    assert len(registry._tools) == 1
    
    # Verify that the second registration overwrote the first
    tool_class = registry.get_tool("same_name")
    assert tool_class == Tool2

def test_get_tool():
    """Test retrieving tools from registry."""
    registry = ToolRegistry()
    registry.register(TestTool1)
    
    # Test getting existing tool
    tool_class = registry.get_tool("test_tool_1")
    assert tool_class == TestTool1
    
    # Test getting non-existent tool
    with pytest.raises(KeyError):
        registry.get_tool("non_existent_tool")

def test_get_all_tools():
    """Test getting all registered tools."""
    registry = ToolRegistry()
    registry.register(TestTool1)
    registry.register(TestTool2)
    
    tools = registry.get_all_tools()
    assert len(tools) == 2
    assert TestTool1 in tools
    assert TestTool2 in tools

def test_get_tool_schemas():
    """Test getting schemas for all tools."""
    registry = ToolRegistry()
    registry.register(TestTool1)
    registry.register(TestTool2)
    
    schemas = registry.get_tool_schemas()
    assert len(schemas) == 2
    
    # Verify schema format
    for schema in schemas:
        assert schema["type"] == "function"
        assert "function" in schema
        assert "name" in schema["function"]
        assert "description" in schema["function"]
        assert "parameters" in schema["function"]

def test_auto_discovery(tmp_path):
    """Test automatic tool discovery from a directory."""
    # Create a temporary tools directory
    tools_dir = tmp_path / "tools"
    tools_dir.mkdir()
    
    # Create a test tool module
    tool_code = '''
from MC.tools.base import BaseTool

class AutoDiscoveredTool(BaseTool):
    name = "auto_tool"
    description = "Automatically discovered tool"
    
    async def execute(self, value: str) -> str:
        return value
'''
    
    with open(tools_dir / "auto_tool.py", "w") as f:
        f.write(tool_code)
    
    # Test loading tools from directory
    registry = ToolRegistry.load_tools(str(tools_dir))
    
    # Note: This test might need adjustment depending on how your module importing works
    # The current implementation might need modifications to work with dynamic imports
    # from arbitrary directories

def test_invalid_tool_registration():
    """Test that invalid tools cannot be registered."""
    registry = ToolRegistry()
    
    # Try to register a class that's not a BaseTool
    class NotATool:
        pass
    
    with pytest.raises(ValueError):
        registry.register(NotATool)
    
    # Try to register a BaseTool without execute method
    class InvalidTool(BaseTool):
        name = "invalid"
    
    with pytest.raises(NotImplementedError):
        registry.register(InvalidTool) 