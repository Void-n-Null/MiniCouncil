"""Base Tool Module - Defines the base class for all tools.

This module provides:
- BaseTool abstract base class
- Tool schema generation
- Parameter validation
- Execution interface
- Common tool utilities
"""

import inspect
from typing import Dict, Any, Optional, Type, get_type_hints, Union

from pydantic import BaseModel, create_model, ValidationError

class BaseTool:
    """Base class for all tools.
    
    All tools must inherit from this class and implement:
    - name: Tool name (class attribute)
    - description: Tool description (class attribute)
    - _execute: Async method that implements the tool's functionality
    
    The class provides:
    - Parameter validation
    - Schema generation
    - Execution interface
    """
    
    name: str = ""  # Tool name (override in subclass)
    description: str = ""  # Tool description (override in subclass)
    
    @classmethod
    def get_parameter_schema(cls) -> Dict[str, Any]:
        """Get the parameter schema for this tool."""
        # Get type hints for _execute method
        hints = get_type_hints(cls._execute)
        
        # Remove return annotation and self parameter
        hints.pop('return', None)
        hints.pop('self', None)
        
        # Create field definitions
        properties = {}
        required = []
        
        for name, type_hint in hints.items():
            # Check if parameter is optional
            is_optional = (
                hasattr(type_hint, '__origin__') and 
                type_hint.__origin__ is Union and 
                type(None) in type_hint.__args__
            )
            
            # Get the actual type (unwrap Optional)
            if is_optional:
                field_type = next(t for t in type_hint.__args__ if t is not type(None))
            else:
                field_type = type_hint
                required.append(name)
            
            # Create field definition
            field_def = {"type": cls._get_json_type(field_type)}
            
            # Add default if parameter has one
            sig = inspect.signature(cls._execute)
            if name in sig.parameters:
                param = sig.parameters[name]
                if param.default is not param.empty:
                    field_def["default"] = param.default
            
            properties[name] = field_def
        
        return {
            "type": "object",
            "properties": properties,
            "required": required
        }
    
    @classmethod
    def get_tool_schema(cls) -> Dict[str, Any]:
        """Get the complete tool schema."""
        return {
            "type": "function",
            "function": {
                "name": cls.name or cls.__name__.lower(),
                "description": cls.description,
                "parameters": cls.get_parameter_schema()
            }
        }
    
    @staticmethod
    def _get_json_type(python_type: Type) -> str:
        """Convert Python type to JSON schema type."""
        type_map = {
            str: "string",
            int: "integer",
            float: "number",
            bool: "boolean",
            list: "array",
            dict: "object"
        }
        return type_map.get(python_type, "string")
    
    async def execute(self, **kwargs) -> Any:
        """
        Execute the tool with validation.
        
        Args:
            **kwargs: Tool parameters
            
        Returns:
            Tool execution result
            
        Raises:
            TypeError: If parameters fail validation
        """
        try:
            # Create a model for validation
            param_model = create_model(
                'ToolParameters',
                **{k: (v, ...) for k, v in get_type_hints(self._execute).items()}
            )
            # Validate parameters
            param_model(**kwargs)
            # Execute tool
            return await self._execute(**kwargs)
        except ValidationError as exc:
            raise TypeError(str(exc)) from exc
    
    async def _execute(self, **kwargs) -> Any:
        """
        Execute the tool's functionality.
        
        Must be implemented by subclasses.
        """
        raise NotImplementedError("Tool must implement _execute method") 