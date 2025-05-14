"""
Configuration management for CLI tools.

This module provides unified handling of configuration from various sources
including files, environment variables, and command-line arguments.
"""

import os
import json
import configparser
from typing import Dict, List, Any, Optional, Union, Callable

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
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            # Recursively merge nested dictionaries
            result[key] = merge_dicts(result[key], value)
        else:
            # Override or add the value
            result[key] = value
            
    return result


def parse_json(content: str) -> Dict:
    """
    Parse JSON content.
    
    Args:
        content (str): JSON content to parse.
        
    Returns:
        Dict: Parsed dictionary or empty dict on failure.
    """
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {}


def parse_ini(content: str) -> Dict:
    """
    Parse INI content.

    Args:
        content (str): INI content to parse.

    Returns:
        Dict: Parsed dictionary or empty dict on failure.
    """
    try:
        parser = configparser.ConfigParser()
        parser.read_string(content)

        result = {}

        # Add default section if not empty
        if parser.defaults():
            result.update(parser.defaults())

        # Add other sections
        for section in parser.sections():
            result[section] = dict(parser[section])

        return result
    except configparser.Error:
        return {}
    

def get_parser_for_extension(extension: str) -> Optional[Callable]:
    """
    Get the appropriate parser function for a file extension.
    
    Args:
        extension (str): File extension (e.g., 'json', 'ini').
        
    Returns:
        Callable or None: Parser function or None if no parser is available.
    """
    parsers = {
        'json': parse_json,
        'ini': parse_ini
    }
    
    # Try optional parsers if available
    try:
        import yaml
        parsers['yaml'] = parsers['yml'] = yaml.safe_load
    except ImportError:
        pass
    
    try:
        import toml
        parsers['toml'] = toml.loads
    except ImportError:
        pass
    
    return parsers.get(extension.lower())


def parse_config_string(content: str, format_type: str) -> Dict:
    """
    Parse a configuration string based on its format.
    
    Args:
        content (str): The configuration content.
        format_type (str): Format type ('json', 'ini', 'yaml', 'toml').
        
    Returns:
        Dict: Parsed configuration or empty dict on failure.
    """
    parser = get_parser_for_extension(format_type)
    
    if parser:
        try:
            result = parser(content)
            if result is None:
                return {}
            return result if isinstance(result, dict) else {}
        except Exception:
            return {}
    
    return {}


def parse_config_file(file_path: str) -> Dict:
    """
    Parse a configuration file based on its extension.
    
    Args:
        file_path (str): Path to the configuration file.
        
    Returns:
        Dict: Parsed configuration or empty dict if file cannot be parsed.
    """
    _, ext = os.path.splitext(file_path)
    ext = ext.lstrip('.')
    
    parser = get_parser_for_extension(ext)
    
    if not parser:
        return {}
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        result = parser(content)
        return result if isinstance(result, dict) else {}
    except (IOError, Exception):
        return {}


def parse_config_files(file_paths: List[str]) -> Dict:
    """
    Parse multiple configuration files and merge them.
    
    Later files in the list take precedence over earlier ones.
    
    Args:
        file_paths (List[str]): List of configuration file paths.
        
    Returns:
        Dict: Merged configuration.
    """
    result = {}
    
    for file_path in file_paths:
        config = parse_config_file(file_path)
        result = merge_dicts(result, config)
    
    return result


def get_env_variables(prefix: str = "") -> Dict:
    """
    Get environment variables, optionally filtered by prefix.
    
    Args:
        prefix (str): Prefix to filter environment variables.
        
    Returns:
        Dict: Dictionary of environment variables.
    """
    result = {}
    
    for key, value in os.environ.items():
        if not prefix or key.startswith(prefix):
            # Remove prefix if specified
            normalized_key = key[len(prefix):] if prefix and key.startswith(prefix) else key
            result[normalized_key] = value
    
    return result