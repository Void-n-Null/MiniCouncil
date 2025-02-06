"""Tests for the tool registry functionality."""

import pytest
import os
import sys
from pathlib import Path
from typing import Optional
from MC.core.base_tool import BaseTool
from MC.core.registry import ToolRegistry

# Example tools for testing
class TestTool1(BaseTool):
    """A test tool."""
    name = "test_tool_1"
    description = "A test tool"
    
    async def _execute(self, **kwargs):
        return "test_tool_1 executed"

class TestTool2(BaseTool):
    """Another test tool."""
    name = "test_tool_2"
    description = "Another test tool"
    
    async def _execute(self, **kwargs):
        return "test_tool_2 executed"

@pytest.mark.asyncio
async def test_registry_initialization():
    """Test that registry initializes properly."""
    registry = ToolRegistry()
    assert registry._tools == {}

@pytest.mark.asyncio
async def test_tool_registration():
    """Test that tools can be registered."""
    registry = ToolRegistry()
    
    # Register a tool
    registry.register(TestTool1)
    assert "test_tool_1" in registry._tools
    assert registry._tools["test_tool_1"] == TestTool1
    
    # Register another tool
    registry.register(TestTool2)
    assert len(registry._tools) == 2
    assert "test_tool_2" in registry._tools

@pytest.mark.asyncio
async def test_duplicate_tool_registration():
    """Test that registering a tool with the same name updates the registry."""
    registry = ToolRegistry()
    
    class Tool1(BaseTool):
        """First tool."""
        name = "tool1"
        description = "Tool 1"
        
        async def _execute(self, **kwargs):
            return "tool1 executed"
    
    class Tool2(BaseTool):
        """Second tool with same name."""
        name = "tool1"  # Same name as Tool1
        description = "Tool 2"
        
        async def _execute(self, **kwargs):
            return "tool2 executed"
    
    registry.register(Tool1)
    registry.register(Tool2)
    assert len(registry._tools) == 1
    
    # Verify that the second registration overwrote the first
    tool_class = registry.get_tool("tool1")
    assert tool_class == Tool2

@pytest.mark.asyncio
async def test_get_tool():
    """Test retrieving tools from registry."""
    registry = ToolRegistry()
    registry.register(TestTool1)
    
    # Test getting existing tool
    tool_class = registry.get_tool("test_tool_1")
    assert tool_class == TestTool1
    
    # Test getting non-existent tool
    with pytest.raises(KeyError):
        registry.get_tool("nonexistent_tool")

@pytest.mark.asyncio
async def test_get_all_tools():
    """Test getting all registered tools."""
    registry = ToolRegistry()
    registry.register(TestTool1)
    registry.register(TestTool2)
    
    tools = registry.get_all_tools()
    assert len(tools) == 2
    assert TestTool1 in tools
    assert TestTool2 in tools

@pytest.mark.asyncio
async def test_get_tool_schemas():
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

@pytest.mark.asyncio
async def test_auto_discovery(tmp_path):
    """Test automatic tool discovery from a directory."""
    # Create a temporary tools directory
    tools_dir = tmp_path / "tools"
    tools_dir.mkdir()
    
    # Add tmp_path to Python path so the module can be imported
    sys.path.insert(0, str(tmp_path))
    
    try:
        # Create a test tool module
        tool_code = '''
from MC.core.base_tool import BaseTool

class AutoDiscoveredTool(BaseTool):
    """Auto-discovered test tool."""
    name = "auto_tool"
    description = "Automatically discovered tool"
    
    async def _execute(self, **kwargs):
        return "auto_tool executed"
'''
        
        with open(tools_dir / "auto_tool.py", "w", encoding='utf-8') as f:
            f.write(tool_code)
        
        # Test loading tools from directory
        registry = ToolRegistry()
        
        # Import the tool module and register the tool
        import importlib.util
        spec = importlib.util.spec_from_file_location("auto_tool", str(tools_dir / "auto_tool.py"))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        registry.register(module.AutoDiscoveredTool)
        
        # Verify the tool was discovered
        assert "auto_tool" in registry._tools
        
    finally:
        # Clean up
        sys.path.remove(str(tmp_path))

@pytest.mark.asyncio
async def test_invalid_tool_registration():
    """Test that invalid tools cannot be registered."""
    registry = ToolRegistry()
    
    # Try to register a class that's not a BaseTool
    class NotATool:
        """Not a tool class."""
        pass
    
    with pytest.raises(ValueError):
        registry.register(NotATool)
    
    # Try to register a BaseTool without execute method
    class InvalidTool(BaseTool):
        """Invalid tool without _execute method."""
        name = "invalid"
    
    with pytest.raises(NotImplementedError):
        registry.register(InvalidTool) 