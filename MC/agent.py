from typing import List, Dict, Any, Optional
from .openrouter_client import OpenRouterClient, Message
from .tools.registry import ToolRegistry
from .tool_executor import ToolExecutor

class Agent:
    """An AI agent that can use tools to accomplish tasks."""
    
    def __init__(self, 
                 name: str, 
                 model: str = "openai/gpt-3.5-turbo", 
                 tools: Optional[List[str]] = None,
                 system_prompt: Optional[str] = None):
        """
        Initialize an agent.
        
        Args:
            name: The name of the agent
            model: The OpenRouter model to use (default: gpt-3.5-turbo)
            tools: List of tool names to make available to the agent (default: all tools)
            system_prompt: Optional system prompt to set the agent's behavior
        """
        self.name = name
        self.model = model
        self.messages: List[Message] = []
        self.client = OpenRouterClient()
        self.tool_executor = ToolExecutor()
        
        # Set up tools
        self.registry = ToolRegistry()
        if tools:
            # Load only specified tools
            self.registry.load_tools()
            available_tools = self.registry.get_all_tools()
            self.registry = ToolRegistry()  # Reset registry
            for tool in available_tools:
                if tool.name in tools:
                    self.registry.register(tool)
        else:
            # Load all tools
            self.registry.load_tools()
        
        # Add system prompt if provided
        if system_prompt:
            self.messages.append(Message(role="system", content=system_prompt))
    
    def add_message(self, content: str, role: str = "user") -> None:
        """Add a message to the conversation."""
        self.messages.append(Message(role=role, content=content))
    
    def add_tool_interaction(self, tool_call: Dict[str, Any], result: str) -> None:
        """Add a tool interaction to the conversation."""
        self.messages.append(Message(
            role="assistant",
            content=None,
            tool_calls=[tool_call]
        ))
        
        self.messages.append(Message(
            role="tool",
            content=result,
            name=tool_call['function']['name'],
            tool_call_id=tool_call['id']
        ))
    
    async def get_response(self, temperature: float = 0.7) -> str:
        """
        Get a response from the agent, handling any tool calls.
        
        Args:
            temperature: Controls randomness in responses (0-2)
            
        Returns:
            The agent's final response
        """
        while True:
            # Get completion from model with tools
            response = self.client.chat_completion(
                messages=self.messages,
                model=self.model,
                tools=self.registry.get_tool_schemas(),
                temperature=temperature
            )
            
            message = response['choices'][0]['message']
            
            # If the model wants to use tools
            if 'tool_calls' in message:
                await self._handle_tool_calls(message['tool_calls'])
                continue
            
            # If no more tool calls, return the final response
            return message['content']
    
    async def _handle_tool_calls(self, tool_calls: list) -> None:
        """Handle tool calls from the model."""
        for tool_call in tool_calls:
            # Execute the tool
            result = await self.tool_executor.execute_tool_call(tool_call)
            
            # Record the interaction
            self.add_tool_interaction(tool_call, result) 