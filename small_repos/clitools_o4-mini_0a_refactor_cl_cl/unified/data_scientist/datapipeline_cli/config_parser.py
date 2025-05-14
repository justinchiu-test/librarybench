"""Configuration parser for data scientist CLI tools."""

import os
import json
import configparser
from typing import Dict, List, Any


def parse_json_file(file_path: str) -> Dict:
    """
    Parse a JSON configuration file.
    
    Args:
        file_path (str): Path to the JSON file.
        
    Returns:
        Dict: Parsed configuration or empty dict if file cannot be parsed.
    """
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError):
        return {}


def parse_ini_file(file_path: str) -> Dict:
    """
    Parse an INI configuration file, returning the 'default' section.
    
    Args:
        file_path (str): Path to the INI file.
        
    Returns:
        Dict: Parsed configuration or empty dict if file cannot be parsed.
    """
    try:
        config = configparser.ConfigParser()
        config.read(file_path)
        
        # Return default section if exists
        if 'default' in config:
            return dict(config['default'])
        elif 'DEFAULT' in config:
            return dict(config['DEFAULT'])
        
        return {}
    except (IOError, configparser.Error):
        return {}


def merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """
    Merge two dictionaries, with dict2 overriding values from dict1.
    
    Args:
        dict1 (Dict): Base dictionary.
        dict2 (Dict): Dictionary with override values.
        
    Returns:
        Dict: Merged dictionary.
    """
    result = dict1.copy()
    result.update(dict2)
    return result


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
        _, ext = os.path.splitext(file_path)
        ext = ext.lstrip('.')
        
        if ext.lower() == 'json':
            config = parse_json_file(file_path)
        elif ext.lower() == 'ini':
            config = parse_ini_file(file_path)
        else:
            config = {}
        
        result = merge_dicts(result, config)
    
    return result