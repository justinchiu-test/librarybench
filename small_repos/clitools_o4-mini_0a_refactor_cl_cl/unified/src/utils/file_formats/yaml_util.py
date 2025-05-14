"""
YAML handling utilities.

This module provides functionality for reading and writing YAML files.
"""

import os
from typing import Dict, List, Any, Optional, Union

# Check if PyYAML is available
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


def load_yaml_file(file_path: str) -> Dict[str, Any]:
    """
    Load a YAML file.
    
    Args:
        file_path (str): Path to the YAML file.
        
    Returns:
        Dict[str, Any]: Parsed YAML data.
        
    Raises:
        ImportError: If PyYAML is not installed.
        FileNotFoundError: If the file does not exist.
        yaml.YAMLError: If the file contains invalid YAML.
    """
    if not YAML_AVAILABLE:
        raise ImportError("PyYAML is not installed. Install it with 'pip install PyYAML'.")
    
    with open(file_path, 'r') as f:
        return yaml.safe_load(f) or {}


def load_yaml_string(content: str) -> Dict[str, Any]:
    """
    Parse a YAML string.
    
    Args:
        content (str): YAML string to parse.
        
    Returns:
        Dict[str, Any]: Parsed YAML data.
        
    Raises:
        ImportError: If PyYAML is not installed.
        yaml.YAMLError: If the string contains invalid YAML.
    """
    if not YAML_AVAILABLE:
        raise ImportError("PyYAML is not installed. Install it with 'pip install PyYAML'.")
    
    return yaml.safe_load(content) or {}


def save_yaml_file(data: Dict[str, Any], file_path: str) -> None:
    """
    Save data to a YAML file.
    
    Args:
        data (Dict[str, Any]): Data to save.
        file_path (str): Output file path.
        
    Raises:
        ImportError: If PyYAML is not installed.
        IOError: If the file cannot be written.
    """
    if not YAML_AVAILABLE:
        raise ImportError("PyYAML is not installed. Install it with 'pip install PyYAML'.")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
    
    with open(file_path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False)


def to_yaml_string(data: Dict[str, Any]) -> str:
    """
    Convert data to a YAML string.
    
    Args:
        data (Dict[str, Any]): Data to convert.
        
    Returns:
        str: YAML string.
        
    Raises:
        ImportError: If PyYAML is not installed.
    """
    if not YAML_AVAILABLE:
        raise ImportError("PyYAML is not installed. Install it with 'pip install PyYAML'.")
    
    return yaml.dump(data, default_flow_style=False)


def yaml_safe_load(file_path: str, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Safely load a YAML file.
    
    Args:
        file_path (str): Path to the YAML file.
        default (Dict[str, Any], optional): Default to return if loading fails.
        
    Returns:
        Dict[str, Any]: Parsed YAML data or default value.
    """
    if not YAML_AVAILABLE:
        return default or {}
    
    try:
        with open(file_path, 'r') as f:
            result = yaml.safe_load(f)
            return result if isinstance(result, dict) else (default or {})
    except (FileNotFoundError, yaml.YAMLError, IOError):
        return default or {}


def yaml_safe_loads(content: str, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Safely parse YAML content.
    
    Args:
        content (str): YAML content to parse.
        default (Dict[str, Any], optional): Default to return if parsing fails.
        
    Returns:
        Dict[str, Any]: Parsed YAML data or default value.
    """
    if not YAML_AVAILABLE:
        return default or {}
    
    try:
        result = yaml.safe_load(content)
        return result if isinstance(result, dict) else (default or {})
    except yaml.YAMLError:
        return default or {}