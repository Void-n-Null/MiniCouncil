import os
from typing import List, Dict, Any, Optional, Union
import requests
from dataclasses import dataclass

@dataclass
class Message:
    role: str
    content: Optional[str]
    name: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None

class OpenRouterClient:
    def __init__(self, api_key: str = None, site_url: str = None, site_name: str = None):
        """
        Initialize the OpenRouter client.
        
        Args:
            api_key: OpenRouter API key. If not provided, will look for OPENROUTER_API_KEY env variable
            site_url: Your site URL for rankings (optional)
            site_name: Your site name for rankings (optional)
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OpenRouter API key must be provided or set in OPENROUTER_API_KEY environment variable")
        
        self.base_url = "https://openrouter.ai/api/v1"
        self.site_url = site_url
        self.site_name = site_name

    def _get_headers(self) -> Dict[str, str]:
        """Get the headers required for OpenRouter API requests."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        if self.site_url:
            headers["HTTP-Referer"] = self.site_url
        if self.site_name:
            headers["X-Title"] = self.site_name
            
        return headers

    def chat_completion(
        self,
        messages: List[Message],
        model: str = "openai/gpt-3.5-turbo",
        tools: Optional[List[Dict[str, Any]]] = None,
        temperature: float = 1.0,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Send a chat completion request to OpenRouter.
        
        Args:
            messages: List of Message objects containing the conversation
            model: Model identifier to use (default: gpt-3.5-turbo)
            tools: Optional list of tools/functions the model can use
            temperature: Controls randomness in responses (0-2)
            max_tokens: Maximum tokens in response
            stream: Whether to stream the response
            
        Returns:
            API response as a dictionary
        """
        url = f"{self.base_url}/chat/completions"
        
        # Convert Message objects to dictionaries
        messages_dict = [
            {
                "role": msg.role,
                "content": msg.content,
                **({"name": msg.name} if msg.name else {}),
                **({"tool_calls": msg.tool_calls} if msg.tool_calls else {}),
                **({"tool_call_id": msg.tool_call_id} if msg.tool_call_id else {})
            }
            for msg in messages
        ]
        
        payload = {
            "model": model,
            "messages": messages_dict,
            "temperature": temperature,
            "stream": stream
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
            
        if tools:
            payload["tools"] = tools
            
        response = requests.post(
            url,
            headers=self._get_headers(),
            json=payload
        )
        response.raise_for_status()
        
        return response.json() 