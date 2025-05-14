"""Configuration parser for backend developer CLI tools."""

import os
import json
import configparser
from typing import Dict, List, Any, Optional, Union, Callable
from src.cli_core.config import parse_config_files as core_parse_config_files

# Re-export the function from core for backward compatibility
def parse_config_files(file_paths: List[str]) -> Dict:
    """
    Parse multiple configuration files and merge them.

    Later files in the list take precedence over earlier ones.

    Args:
        file_paths (List[str]): List of configuration file paths.

    Returns:
        Dict: Merged configuration.
    """
    return core_parse_config_files(file_paths)