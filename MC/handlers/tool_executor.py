"""Tool Executor Module - Handles tool execution and result processing.

This module provides the ToolExecutor class which:
- Executes tool calls from the model
- Processes tool arguments
- Handles tool execution errors
- Returns formatted results
"""

import json
from typing import Dict, Any
from ..core.registry import GLOBAL_REGISTRY
from ..tools.file_tools import FileToolError

class ToolExecutionError(Exception):
    """Exception raised when tool execution fails."""

class ToolExecutor:
    """Handles tool execution and result processing."""
    
    async def execute_tool_call(self, tool_call: Dict[str, Any]) -> str:
        """
        Execute a tool call and return the result.
        
        Args:
            tool_call: The tool call to execute
            
        Returns:
            The result of the tool execution
            
        Raises:
            ToolExecutionError: If tool execution fails
        """
        function_name = tool_call['function']['name']
        
        try:
            arguments = json.loads(tool_call['function']['arguments'])
        except json.JSONDecodeError as exc:
            raise ToolExecutionError(
                f"Invalid JSON in arguments for {function_name}"
            ) from exc
        
        try:
            # Get the tool class from registry
            tool_class = GLOBAL_REGISTRY.get_tool(function_name)
            # Create an instance and execute
            tool = tool_class()
            result = await tool.execute(**arguments)
            return json.dumps(result) if isinstance(result, dict) else str(result)
            
        except KeyError as exc:
            raise ToolExecutionError(
                f"Unknown function {function_name}"
            ) from exc
        except (TypeError, ValueError) as exc:
            raise ToolExecutionError(
                f"Invalid arguments for {function_name}: {str(exc)}"
            ) from exc
        except FileToolError as exc:
            raise ToolExecutionError(
                f"File operation error in {function_name}: {str(exc)}"
            ) from exc
        except NotImplementedError as exc:
            raise ToolExecutionError(
                f"Tool {function_name} not properly implemented: {str(exc)}"
            ) from exc
        except Exception as exc:
            raise ToolExecutionError(
                f"Unexpected error executing {function_name}: {str(exc)}"
            ) from exc 