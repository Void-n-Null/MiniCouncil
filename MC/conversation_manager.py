from typing import Dict, Any, Optional
from .openrouter_client import OpenRouterClient
from .message_handler import MessageHandler
from .tool_executor import ToolExecutor
from .tools.registry import registry

class ConversationManager:
    """Manages the overall conversation flow and coordinates components."""
    
    def __init__(self):
        self.client = OpenRouterClient()
        self.message_handler = MessageHandler()
        self.tool_executor = ToolExecutor()
    
    async def process_conversation(self, initial_prompt: str) -> str:
        """Process a conversation from initial prompt to final response."""
        # Add the initial user message
        self.message_handler.add_user_message(initial_prompt)
        
        while True:
            # Get completion from model with tools
            response = self.client.chat_completion(
                messages=self.message_handler.messages,
                model="openai/gpt-3.5-turbo",
                tools=registry.get_tool_schemas(),
                temperature=0.7
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
            self.message_handler.add_tool_interaction(tool_call, result) 