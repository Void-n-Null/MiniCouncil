"""Core Module - Base classes and fundamental functionality

This directory contains:
- Base classes for tools and handlers
- Core application logic
- Common utilities and abstractions
- Foundational interfaces and protocols
- Tool registry system
- Agent implementation

Files in this directory should be fundamental building blocks that other modules depend on,
but should not depend on other modules themselves (except for external libraries).
"""

from .base_tool import BaseTool
from .path_handler import PathHandler, PathValidationError
from .encoding import EncodingHandler
from .registry import ToolRegistry, GLOBAL_REGISTRY
from .agent import Agent

__all__ = [
    'BaseTool',
    'PathHandler',
    'PathValidationError',
    'EncodingHandler',
    'ToolRegistry',
    'GLOBAL_REGISTRY',
    'Agent'
] 