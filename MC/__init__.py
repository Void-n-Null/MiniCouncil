"""Mini Council - A Python package for easy interaction with OpenRouter API

Directory Structure:
- MC/
  ├── api/          # API client and related functionality
  ├── core/         # Core application logic and base classes
  ├── tools/        # Tool implementations and utilities
  ├── config/       # Configuration and settings
  ├── handlers/     # Message and tool execution handlers
  └── cli/          # Command-line interface components
"""

import os
from dotenv import load_dotenv
from .config import setup_logging

# Load environment variables from .env file
load_dotenv()

# Version of the MC package
__version__ = "0.1.0"

# Set up logging when the package is imported
setup_logging()
