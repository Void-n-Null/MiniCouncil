"""Registry Module - Tool registration and management system.

This module provides:
- A central registry for all available tools
- Tool discovery and loading
- Tool validation and registration
- Access to tool schemas
"""

import os
import importlib
import inspect
from typing import Dict, Type, List
from .base_tool import BaseTool

class ToolRegistry:
    """Registry for all available tools."""
    
    def __init__(self):
        """Initialize an empty tool registry."""
        self._tools: Dict[str, Type[BaseTool]] = {}
        
    def register(self, tool_class: Type[BaseTool]) -> None:
        """
        Register a tool class.
        
        Args:
            tool_class: The tool class to register
            
        Raises:
            ValueError: If tool_class is not a BaseTool subclass
            NotImplementedError: If tool_class doesn't implement required methods
        """
        if not issubclass(tool_class, BaseTool):
            raise ValueError(f"{tool_class.__name__} must inherit from BaseTool")
        
        # Verify the tool has an _execute method
        if not hasattr(tool_class, '_execute'):
            raise NotImplementedError(
                f"{tool_class.__name__} must implement _execute method"
            )
        
        # Get the base class's execute method
        base_execute = getattr(BaseTool, '_execute')
        # Get the tool's execute method
        tool_execute = getattr(tool_class, '_execute')
        
        # Verify _execute method is properly implemented
        if tool_execute.__func__ is base_execute.__func__:
            raise NotImplementedError(
                f"{tool_class.__name__} must implement its own _execute method"
            )
        
        tool_name = tool_class.name or tool_class.__name__.lower()
        self._tools[tool_name] = tool_class
    
    def get_tool(self, name: str) -> Type[BaseTool]:
        """
        Get a tool class by name.
        
        Args:
            name: Name of the tool to get
            
        Returns:
            The tool class
            
        Raises:
            KeyError: If tool is not found
        """
        if name not in self._tools:
            raise KeyError(f"Tool {name} not found")
        return self._tools[name]
    
    def get_all_tools(self) -> List[Type[BaseTool]]:
        """Get all registered tools."""
        return list(self._tools.values())
    
    def get_tool_schemas(self) -> List[Dict]:
        """Get schemas for all registered tools."""
        return [tool.get_tool_schema() for tool in self._tools.values()]
    
    @classmethod
    def load_tools(cls, tools_dir: str = None) -> 'ToolRegistry':
        """
        Create a registry and load all tools from the specified directory.
        
        Args:
            tools_dir: Directory to load tools from (default: current directory)
            
        Returns:
            A new ToolRegistry instance with loaded tools
        """
        tool_registry = cls()
        
        if tools_dir is None:
            tools_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Get all Python files in the directory
        for filename in os.listdir(tools_dir):
            if filename.endswith('.py') and not filename.startswith('__'):
                module_name = filename[:-3]  # Remove .py extension
                
                # Import the module
                module_path = f"MC.tools.{module_name}"
                try:
                    module = importlib.import_module(module_path)
                    
                    # Find all Tool classes in the module
                    for _, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and 
                            issubclass(obj, BaseTool) and 
                            obj != BaseTool):
                            tool_registry.register(obj)
                except ImportError as exc:
                    print(f"Error loading module {module_name}: {exc}")
        
        return tool_registry

# Create a global registry instance
GLOBAL_REGISTRY = ToolRegistry.load_tools() 