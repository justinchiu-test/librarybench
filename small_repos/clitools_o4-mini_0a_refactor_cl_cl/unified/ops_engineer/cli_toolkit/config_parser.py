"""Configuration parser for operations engineer CLI tools."""

import os
import json
import configparser
from typing import Dict, List, Any, Optional, Union, Callable
from src.cli_core.config import parse_config_string as core_parse_config_string
from src.cli_core.config import merge_dicts as core_merge_dicts

# Re-export functions from core for backward compatibility
def parse_config_string(content: str, format_type: str) -> Dict:
    """
    Parse a configuration string based on its format.

    Args:
        content (str): The configuration content.
        format_type (str): Format type ('json', 'ini', 'yaml', 'toml').

    Returns:
        Dict: Parsed configuration or empty dict on failure.
    """
    return core_parse_config_string(content, format_type)

def merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """
    Deep merge two dictionaries.

    The second dictionary's values take precedence in case of conflicts.

    Args:
        dict1 (Dict): First dictionary.
        dict2 (Dict): Second dictionary (overrides values from dict1).

    Returns:
        Dict: Merged dictionary.
    """
    return core_merge_dicts(dict1, dict2)