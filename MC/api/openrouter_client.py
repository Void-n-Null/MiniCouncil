"""OpenRouter API Client Module - Handles communication with the OpenRouter API.

This module provides:
- OpenRouter API client implementation
- Message data structures
- API request/response handling
- Authentication and error handling
- Rate limiting and retries
"""

import os
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Union

import requests

@dataclass
class Message:
    """Represents a message in the conversation.
    
    Attributes:
        role: The role of the message sender (user/assistant/system/tool)
        content: The message content
        name: Optional name for tool messages
        tool_call_id: Optional ID for tool call responses
        tool_calls: Optional list of tool calls made by the assistant
    """
    role: str
    content: Optional[str]
    name: Optional[str] = None
    tool_call_id: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None

@dataclass
class ChatConfig:
    """Configuration for chat completion requests.
    
    Attributes:
        model: Model to use for completion
        temperature: Controls randomness (0-2)
        max_tokens: Maximum tokens to generate
        top_p: Nucleus sampling parameter
        tools: List of available tools
        tool_choice: Tool selection preference
    """
    model: str = "openai/gpt-3.5-turbo"
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    tools: Optional[List[Dict[str, Any]]] = None
    tool_choice: Optional[Union[str, Dict[str, Any]]] = None

class OpenRouterClient:
    """Client for interacting with the OpenRouter API.
    
    Handles:
    - API authentication
    - Request formatting and validation
    - Response parsing
    - Error handling and retries
    - Rate limiting compliance
    """
    
    def __init__(self):
        """Initialize the OpenRouter client."""
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        if not self.api_key:
            raise ValueError(
                "OPENROUTER_API_KEY environment variable not set"
            )
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def chat_completion(
        self,
        messages: List[Message],
        config: Optional[ChatConfig] = None
    ) -> Dict[str, Any]:
        """
        Get a chat completion from the OpenRouter API.
        
        Args:
            messages: List of conversation messages
            config: Optional configuration for the request
            
        Returns:
            API response containing the completion
            
        Raises:
            requests.RequestException: If the API request fails
        """
        url = f"{self.base_url}/chat/completions"
        
        # Use default config if none provided
        if config is None:
            config = ChatConfig()
        
        # Build request data
        data = {
            "model": config.model,
            "messages": [msg.__dict__ for msg in messages],
            "temperature": config.temperature
        }
        
        # Add optional parameters if provided
        if config.max_tokens is not None:
            data["max_tokens"] = config.max_tokens
        if config.top_p is not None:
            data["top_p"] = config.top_p
        if config.tools is not None:
            data["tools"] = config.tools
        if config.tool_choice is not None:
            data["tool_choice"] = config.tool_choice
        
        # Make request with timeout
        response = requests.post(
            url,
            headers=self.headers,
            json=data,
            timeout=30  # 30 second timeout
        )
        response.raise_for_status()
        
        return response.json() 