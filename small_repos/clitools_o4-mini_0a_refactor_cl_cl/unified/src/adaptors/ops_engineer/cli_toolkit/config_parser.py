"""
Operations engineer config parser adapter.

Provides backward compatibility for ops_engineer.cli_toolkit.config_parser.
"""

from typing import Dict, Any

from ....cli_core.config import parse_config_string as core_parse_config_string
from ....cli_core.config import merge_dicts as core_merge_dicts


def parse_config_string(content: str, format_type: str) -> Dict[str, Any]:
    """
    Parse a configuration string based on its format.
    
    Args:
        content (str): The configuration content.
        format_type (str): Format type ('json', 'ini', 'yaml', 'toml').
        
    Returns:
        Dict[str, Any]: Parsed configuration.
    """
    return core_parse_config_string(content, format_type)


def merge_dicts(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep merge two dictionaries.
    
    Args:
        dict1 (Dict[str, Any]): First dictionary.
        dict2 (Dict[str, Any]): Second dictionary (overrides values from dict1).
        
    Returns:
        Dict[str, Any]: Merged dictionary.
    """
    return core_merge_dicts(dict1, dict2)