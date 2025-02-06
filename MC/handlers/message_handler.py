"""Message Handler Module - Handles message operations and maintains conversation state.

This module provides the MessageHandler class which:
- Manages the conversation history
- Adds user and assistant messages
- Records tool interactions
- Maintains the message sequence
"""

from typing import List, Dict, Any
from ..api.openrouter_client import Message

class MessageHandler:
    """Handles message operations and maintains conversation state."""
    
    def __init__(self):
        self._messages: List[Message] = []
    
    def add_user_message(self, content: str) -> None:
        """Add a user message to the conversation."""
        self._messages.append(Message(role="user", content=content))
    
    def add_tool_interaction(self, tool_call: Dict[str, Any], result: str) -> None:
        """Add a tool interaction (call and result) to the conversation."""
        self._messages.append(Message(
            role="assistant",
            content=None,
            tool_calls=[tool_call]
        ))
        
        self._messages.append(Message(
            role="tool",
            content=result,
            name=tool_call['function']['name'],
            tool_call_id=tool_call['id']
        ))
    
    def add_assistant_message(self, content: str) -> None:
        """Add an assistant message to the conversation."""
        self._messages.append(Message(role="assistant", content=content))
    
    @property
    def messages(self) -> List[Message]:
        """Get all messages in the conversation."""
        return self._messages.copy()  # Return a copy to prevent external modification 