"""Configuration Module - Handles application configuration and logging setup.

This module provides functionality for:
- Loading and managing logging configuration
- Setting up logging handlers and formatters
- Managing environment-based configuration
- Ensuring log directories exist
"""

import os
import logging.config
from pathlib import Path
import yaml

def setup_logging(
    default_path='config/logging.yaml',
    default_level=logging.INFO,
    env_key='MC_LOG_CONFIG'
):
    """Setup logging configuration.
    
    Args:
        default_path: Path to the logging configuration file
        default_level: Default logging level if config file is not found
        env_key: Environment variable that can override the config file path
    """
    path = os.getenv(env_key, default_path)
    path = Path(__file__).parent / path

    if path.exists():
        with open(path, 'rt', encoding='utf-8') as f:
            try:
                config = yaml.safe_load(f.read())
                # Ensure log directories exist
                for handler in config.get('handlers', {}).values():
                    if 'filename' in handler:
                        log_dir = Path(handler['filename']).parent
                        log_dir.mkdir(parents=True, exist_ok=True)
                
                logging.config.dictConfig(config)
            except (yaml.YAMLError, OSError) as e:
                print(f'Error in logging configuration: {e}')
                print('Using default logging configuration')
                logging.basicConfig(level=default_level)
    else:
        logging.basicConfig(level=default_level)
        print(f'Config file not found at {path}. Using default logging configuration') 