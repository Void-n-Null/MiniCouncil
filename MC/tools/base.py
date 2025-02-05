from typing import Optional, Dict, Any, Type, get_type_hints
from pydantic import BaseModel, create_model
import inspect

class BaseTool:
    """Base class for all tools."""
    name: str = ""
    description: str = ""
    
    @classmethod
    def get_parameter_schema(cls) -> Dict[str, Any]:
        """Generate JSON Schema for the tool's execute method parameters."""
        # Get the execute method
        execute_method = getattr(cls, 'execute', None)
        if not execute_method:
            raise NotImplementedError("Tool must implement execute method")
        
        # Get type hints and signature
        hints = get_type_hints(execute_method)
        sig = inspect.signature(execute_method)
        
        # Create a Pydantic model dynamically from the execute method's parameters
        fields = {}
        for param_name, param in sig.parameters.items():
            if param_name == 'self':  # Skip self parameter
                continue
            
            field_type = hints.get(param_name, Any)
            default = ... if param.default == param.empty else param.default
            fields[param_name] = (field_type, default)
        
        # Create a Pydantic model for parameters
        param_model = create_model(f'{cls.__name__}Parameters', **fields)
        
        # Convert Pydantic model to JSON Schema
        schema = param_model.model_json_schema()
        
        # Format for OpenRouter tool schema
        return {
            "type": "object",
            "properties": schema.get("properties", {}),
            "required": schema.get("required", [])
        }
    
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
        raise NotImplementedError("Tool must implement execute method") 