import json
from typing import Dict, Any
from .tools.registry import registry

class ToolExecutor:
    """Handles tool execution and result processing."""
    
    async def execute_tool_call(self, tool_call: Dict[str, Any]) -> str:
        """Execute a tool call and return the result."""
        function_name = tool_call['function']['name']
        
        try:
            arguments = json.loads(tool_call['function']['arguments'])
        except json.JSONDecodeError:
            return f"Error: Invalid JSON in arguments for {function_name}"
        
        try:
            # Get the tool class from registry
            tool_class = registry.get_tool(function_name)
            # Create an instance and execute
            tool = tool_class()
            result = await tool.execute(**arguments)
            return json.dumps(result) if isinstance(result, dict) else str(result)
        except KeyError:
            return f"Error: Unknown function {function_name}"
        except Exception as e:
            return f"Error executing {function_name}: {str(e)}" 