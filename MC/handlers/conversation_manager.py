"""Conversation Manager Module - Manages the overall conversation flow.

This module provides the ConversationManager class which:
- Coordinates between the API client, message handler, and tool executor
- Manages the conversation state
- Processes model responses and tool calls
- Handles the conversation flow
"""

from typing import Dict, Any, Optional
from ..api.openrouter_client import OpenRouterClient, ChatConfig
from .message_handler import MessageHandler
from .tool_executor import ToolExecutor
from ..core.registry import GLOBAL_REGISTRY

class ConversationManager:
    """Manages the overall conversation flow and coordinates components."""
    
    def __init__(self):
        """Initialize conversation manager components."""
        self.client = OpenRouterClient()
        self.message_handler = MessageHandler()
        self.tool_executor = ToolExecutor()
    
    async def process_conversation(self, initial_prompt: str) -> str:
        """
        Process a conversation from initial prompt to final response.
        
        Args:
            initial_prompt: The initial user message
            
        Returns:
            The final response from the model
        """
        # Add the initial user message
        self.message_handler.add_user_message(initial_prompt)
        
        while True:
            # Create chat config
            config = ChatConfig(
                tools=GLOBAL_REGISTRY.get_tool_schemas()
            )
            
            # Get completion from model with tools
            response = self.client.chat_completion(
                messages=self.message_handler.messages,
                config=config
            )
            
            message = response['choices'][0]['message']
            
            # If the model wants to use tools
            if 'tool_calls' in message:
                await self._handle_tool_calls(message['tool_calls'])
                continue
            
            # If no more tool calls, return the final response
            return message['content']
    
    async def _handle_tool_calls(self, tool_calls: list) -> None:
        """
        Handle tool calls from the model.
        
        Args:
            tool_calls: List of tool calls to execute
        """
        for tool_call in tool_calls:
            # Execute the tool
            result = await self.tool_executor.execute_tool_call(tool_call)
            
            # Record the interaction
            self.message_handler.add_tool_interaction(tool_call, result) 