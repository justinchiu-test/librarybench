"""
Data Export Utilities for cli_form

This module provides functions for exporting form data in various formats.
"""

import json
import os
import datetime
from typing import Dict, Any, Optional

try:
    import yaml
except ImportError:
    yaml = None


def export_as_json(data, file_path=None, pretty=True):
    """
    Export form data as JSON.
    
    Args:
        data (dict): Form data to export
        file_path (str, optional): Path to output file
        pretty (bool): Whether to format with indentation
        
    Returns:
        str: JSON string
    """
    indent = 2 if pretty else None
    json_data = json.dumps(data, indent=indent, default=_json_default)
    
    if file_path:
        with open(file_path, 'w') as f:
            f.write(json_data)
            
    return json_data


def export_as_yaml(data, file_path=None):
    """
    Export form data as YAML.
    
    Args:
        data (dict): Form data to export
        file_path (str, optional): Path to output file
        
    Returns:
        str: YAML string
        
    Raises:
        ImportError: If PyYAML is not installed
    """
    if yaml is None:
        raise ImportError("PyYAML is required for YAML export. Install with 'pip install PyYAML'")
        
    yaml_data = yaml.dump(data, default_flow_style=False)
    
    if file_path:
        with open(file_path, 'w') as f:
            f.write(yaml_data)
            
    return yaml_data


def export_as_dict(data):
    """
    Export form data as a Python dictionary.
    
    Args:
        data (dict): Form data to export
        
    Returns:
        dict: Exported dictionary
    """
    # Make a deep copy to ensure original data isn't modified
    return json.loads(json.dumps(data, default=_json_default))


def export_as_env_vars(data, file_path=None, prefix=''):
    """
    Export form data as environment variables.
    
    Args:
        data (dict): Form data to export
        file_path (str, optional): Path to output file
        prefix (str): Prefix for variable names
        
    Returns:
        str: Environment variables string
    """
    lines = []
    
    for key, value in _flatten_dict(data, prefix).items():
        # Convert key to uppercase, replace spaces with underscores
        env_key = key.upper().replace(' ', '_')
        
        # Quote string values
        if isinstance(value, str):
            value = f'"{value}"'
        elif isinstance(value, bool):
            value = str(value).lower()
        else:
            value = str(value)
            
        lines.append(f"export {env_key}={value}")
        
    env_str = '\n'.join(lines)
    
    if file_path:
        with open(file_path, 'w') as f:
            f.write(env_str)
            
    return env_str


def export_as_ini(data, file_path=None, section='form'):
    """
    Export form data as INI format.
    
    Args:
        data (dict): Form data to export
        file_path (str, optional): Path to output file
        section (str): INI section name
        
    Returns:
        str: INI string
    """
    lines = [f"[{section}]"]
    
    for key, value in _flatten_dict(data).items():
        # Convert value to string
        if isinstance(value, bool):
            value = str(value).lower()
        elif isinstance(value, (list, dict)):
            value = json.dumps(value, default=_json_default)
        else:
            value = str(value)
            
        lines.append(f"{key} = {value}")
        
    ini_str = '\n'.join(lines)
    
    if file_path:
        with open(file_path, 'w') as f:
            f.write(ini_str)
            
    return ini_str


def export_data(data, format='json', file_path=None, **kwargs):
    """
    Export form data in the specified format.
    
    Args:
        data (dict): Form data to export
        format (str): Export format ('json', 'yaml', 'dict', 'env', 'ini')
        file_path (str, optional): Path to output file
        **kwargs: Additional format-specific options
        
    Returns:
        Any: Exported data
        
    Raises:
        ValueError: If format is not supported
    """
    format = format.lower()
    
    if format == 'json':
        return export_as_json(data, file_path, kwargs.get('pretty', True))
    elif format == 'yaml':
        return export_as_yaml(data, file_path)
    elif format == 'dict':
        return export_as_dict(data)
    elif format == 'env':
        return export_as_env_vars(data, file_path, kwargs.get('prefix', ''))
    elif format == 'ini':
        return export_as_ini(data, file_path, kwargs.get('section', 'form'))
    else:
        raise ValueError(f"Unsupported export format: {format}")


def _json_default(obj):
    """JSON serializer for objects not serializable by default."""
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    elif isinstance(obj, datetime.date):
        return obj.isoformat()
    elif isinstance(obj, datetime.time):
        return obj.isoformat()
    elif hasattr(obj, 'to_dict'):
        return obj.to_dict()
    elif hasattr(obj, '__dict__'):
        return {key: value for key, value in obj.__dict__.items() 
                if not key.startswith('_')}
    
    raise TypeError(f"Type {type(obj)} not serializable")


def _flatten_dict(d, parent_key='', sep='_'):
    """Flatten a nested dictionary."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        
        if isinstance(v, dict):
            items.extend(_flatten_dict(v, new_key, sep).items())
        else:
            items.append((new_key, v))
            
    return dict(items)