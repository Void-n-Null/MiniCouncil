import pytest
from typing import Optional
from MC.tools.base import BaseTool

# Example tool classes for testing
class SimpleTestTool(BaseTool):
    """A simple test tool."""
    name = "simple_test"
    description = "A tool for testing"
    
    async def _execute(self, text: str) -> str:
        """Simple echo function."""
        return text

class ComplexTestTool(BaseTool):
    """A more complex test tool."""
    name = "complex_test"
    description = "A tool for testing complex parameters"
    
    async def _execute(self, required_param: str, optional_param: Optional[int] = 42) -> dict:
        """Test function with optional parameters."""
        return {
            "required": required_param,
            "optional": optional_param
        }

class NoNameTool(BaseTool):
    """A tool without an explicit name."""
    async def _execute(self, value: str) -> str:
        return value

def test_tool_name_and_description():
    """Test that tool names and descriptions are properly set."""
    simple_tool = SimpleTestTool()
    assert simple_tool.name == "simple_test"
    assert simple_tool.description == "A tool for testing"
    
    # Test default name generation
    no_name_tool = NoNameTool()
    assert no_name_tool.name == "" # Default empty string
    assert NoNameTool.get_tool_schema()['function']['name'] == "nonametool"

def test_parameter_schema_generation():
    """Test that parameter schemas are correctly generated."""
    # Test simple tool schema
    simple_schema = SimpleTestTool.get_parameter_schema()
    assert simple_schema["type"] == "object"
    assert "text" in simple_schema["properties"]
    assert simple_schema["properties"]["text"]["type"] == "string"
    assert "text" in simple_schema["required"]
    
    # Test complex tool schema
    complex_schema = ComplexTestTool.get_parameter_schema()
    assert "required_param" in complex_schema["properties"]
    assert "optional_param" in complex_schema["properties"]
    assert complex_schema["properties"]["optional_param"]["type"] == "integer"
    assert complex_schema["properties"]["optional_param"]["default"] == 42
    assert "required_param" in complex_schema["required"]
    assert "optional_param" not in complex_schema["required"]

def test_tool_schema_format():
    """Test that the complete tool schema matches OpenRouter's format."""
    schema = SimpleTestTool.get_tool_schema()
    
    assert schema["type"] == "function"
    assert "function" in schema
    assert "name" in schema["function"]
    assert "description" in schema["function"]
    assert "parameters" in schema["function"]
    
    function_schema = schema["function"]
    assert function_schema["name"] == "simple_test"
    assert function_schema["description"] == "A tool for testing"
    assert function_schema["parameters"]["type"] == "object"

@pytest.mark.asyncio
async def test_tool_execution():
    """Test that tools can be executed with proper parameters."""
    simple_tool = SimpleTestTool()
    result = await simple_tool.execute(text="hello")
    assert result == "hello"
    
    complex_tool = ComplexTestTool()
    # Test with only required parameter
    result = await complex_tool.execute(required_param="test")
    assert result["required"] == "test"
    assert result["optional"] == 42
    
    # Test with both parameters
    result = await complex_tool.execute(required_param="test", optional_param=100)
    assert result["required"] == "test"
    assert result["optional"] == 100

@pytest.mark.asyncio
async def test_tool_execution_validation():
    """Test that tools properly validate their parameters."""
    complex_tool = ComplexTestTool()
    
    # Test missing required parameter
    with pytest.raises(TypeError):
        await complex_tool.execute()
    
    # Test wrong type for optional parameter
    with pytest.raises(TypeError):
        await complex_tool.execute(required_param="test", optional_param="not an integer") 