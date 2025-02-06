from typing import Optional, Dict, Any, Type, get_type_hints, Union
from pydantic import BaseModel, create_model, ValidationError
import inspect

class BaseTool:
    """Base class for all tools."""
    name: str = ""
    description: str = ""
    
    @classmethod
    def get_parameter_schema(cls) -> Dict[str, Any]:
        """Generate JSON Schema for the tool's execute method parameters."""
        # Get the execute method
        execute_method = getattr(cls, '_execute', None)
        if not execute_method:
            raise NotImplementedError("Tool must implement _execute method")
        
        # Get type hints and signature
        hints = get_type_hints(execute_method)
        sig = inspect.signature(execute_method)
        
        # Format for OpenRouter tool schema
        properties = {}
        required = []
        
        for param_name, param in sig.parameters.items():
            if param_name == 'self':  # Skip self parameter
                continue
            
            param_type = hints.get(param_name, Any)
            param_info = {
                "type": cls._get_json_type(param_type),
                "description": ""  # Could extract from docstring in future
            }
            
            # Add default if present
            if param.default is not param.empty:
                param_info["default"] = param.default
            else:
                required.append(param_name)
            
            properties[param_name] = param_info
        
        return {
            "type": "object",
            "properties": properties,
            "required": required
        }
    
    @staticmethod
    def _get_json_type(python_type: Type) -> str:
        """Convert Python types to JSON Schema types."""
        # Handle Optional types
        if getattr(python_type, "__origin__", None) == Union:
            args = getattr(python_type, "__args__", ())
            if type(None) in args:
                # Get the non-None type
                python_type = next(t for t in args if t != type(None))
        
        # Get the actual type
        if hasattr(python_type, "__origin__"):
            python_type = python_type.__origin__
        
        type_mapping = {
            str: "string",
            int: "integer",
            float: "number",
            bool: "boolean",
            list: "array",
            dict: "object",
            Any: "string",  # Default to string for Any
        }
        
        return type_mapping.get(python_type, "string")
    
    @classmethod
    def get_tool_schema(cls) -> Dict[str, Any]:
        """Get the complete tool schema for OpenRouter."""
        return {
            "type": "function",
            "function": {
                "name": cls.name or cls.__name__.lower(),
                "description": cls.description or cls.__doc__ or "",
                "parameters": cls.get_parameter_schema()
            }
        }
    
    async def execute(self, **kwargs) -> Any:
        """Execute the tool with the given parameters."""
        # Get the parameter model for validation
        hints = get_type_hints(self._execute)
        sig = inspect.signature(self._execute)
        
        fields = {}
        for param_name, param in sig.parameters.items():
            if param_name == 'self':  # Skip self parameter
                continue
            
            field_type = hints.get(param_name, Any)
            default = ... if param.default == param.empty else param.default
            fields[param_name] = (field_type, default)
        
        # Create a Pydantic model for parameters
        param_model = create_model(f'{self.__class__.__name__}Parameters', **fields)
        
        try:
            # Validate parameters
            validated_params = param_model(**kwargs)
            return await self._execute(**validated_params.model_dump())
        except ValidationError as e:
            raise TypeError(str(e))
    
    async def _execute(self, **kwargs) -> Any:
        """
        Internal execute method that subclasses should implement.
        This allows us to wrap the execute method with validation while keeping
        the interface clean for subclasses.
        """
        raise NotImplementedError("Tool must implement _execute method") 