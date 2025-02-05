import os
import importlib
import inspect
from typing import Dict, Type, List
from .base import BaseTool

class ToolRegistry:
    """Registry for all available tools."""
    
    def __init__(self):
        self._tools: Dict[str, Type[BaseTool]] = {}
        
    def register(self, tool_class: Type[BaseTool]) -> None:
        """Register a tool class."""
        if not issubclass(tool_class, BaseTool):
            raise ValueError(f"{tool_class.__name__} must inherit from BaseTool")
        
        tool_name = tool_class.name or tool_class.__name__.lower()
        self._tools[tool_name] = tool_class
    
    def get_tool(self, name: str) -> Type[BaseTool]:
        """Get a tool class by name."""
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
        If no directory is specified, uses the current directory.
        """
        registry = cls()
        
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
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and 
                            issubclass(obj, BaseTool) and 
                            obj != BaseTool):
                            registry.register(obj)
                except Exception as e:
                    print(f"Error loading module {module_name}: {e}")
        
        return registry

# Create a global registry instance
registry = ToolRegistry.load_tools() 