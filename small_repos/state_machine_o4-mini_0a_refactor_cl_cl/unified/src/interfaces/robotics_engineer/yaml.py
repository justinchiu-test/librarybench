"""
Simple YAML parser and dumper for the robotics engineer interface.
This module provides a minimal implementation for YAML processing,
focusing only on what's needed for the state machine serialization.
"""

from typing import Any, Dict, List, Optional, Union
import re


def safe_load(yaml_str: str) -> Union[Dict[str, Any], List[Any]]:
    """
    Parse a YAML string into a Python data structure.

    Args:
        yaml_str: YAML string to parse

    Returns:
        Parsed Python data structure (dict or list)
    """
    lines = yaml_str.split('\n')
    return _parse_yaml(lines)


def safe_dump(data: Union[Dict[str, Any], List[Any]], indent: int = 2) -> str:
    """
    Convert a Python data structure to a YAML string.

    Args:
        data: Python data structure to convert
        indent: Number of spaces to use for indentation

    Returns:
        YAML string representation
    """
    return _dump_yaml(data, indent)


def _parse_yaml(lines: List[str]) -> Union[Dict[str, Any], List[Any]]:
    """
    Parse YAML lines into a Python data structure.
    
    Args:
        lines: List of YAML lines

    Returns:
        Parsed Python data structure
    """
    if not lines or all(not line.strip() or line.strip().startswith('#') for line in lines):
        return {}

    # Check if this is a list or dict at the root
    first_line = next((l for l in lines if l.strip() and not l.strip().startswith('#')), '')
    is_list = first_line.strip().startswith('- ')
    
    if is_list:
        return _parse_yaml_list(lines)
    else:
        return _parse_yaml_dict(lines)


def _parse_yaml_dict(lines: List[str], base_indent: int = 0) -> Dict[str, Any]:
    """
    Parse YAML lines into a dictionary.
    
    Args:
        lines: List of YAML lines
        base_indent: Base indentation level

    Returns:
        Parsed dictionary
    """
    result = {}
    key = None
    value_lines = []
    nested_indent = None
    
    for i, line in enumerate(lines):
        if not line.strip() or line.strip().startswith('#'):
            continue
            
        # Calculate line indentation
        indent = len(line) - len(line.lstrip())
        if indent < base_indent:
            break
            
        if indent == base_indent and ':' in line:
            # Process previous key-value pair if it exists
            if key is not None:
                if value_lines:
                    if nested_indent is not None:
                        # Parse nested structure
                        nested_lines = [l[nested_indent - base_indent:] for l in value_lines]
                        if value_lines[0].lstrip().startswith('- '):
                            result[key] = _parse_yaml_list(nested_lines)
                        else:
                            result[key] = _parse_yaml_dict(nested_lines, 0)
                    else:
                        # Single-line value
                        value = value_lines[0].strip()
                        result[key] = _convert_value(value)
                else:
                    # Empty value
                    result[key] = None

            # Parse new key
            parts = line.split(':', 1)
            key = parts[0].strip()
            value_part = parts[1].strip() if len(parts) > 1 else ''
            
            if value_part:
                # Inline value
                result[key] = _convert_value(value_part)
                key = None
                value_lines = []
                nested_indent = None
            else:
                # Prepare for multi-line or nested value
                value_lines = []
                nested_indent = None
        
        elif key is not None and indent > base_indent:
            # Collect value lines for current key
            value_lines.append(line)
            
            # Track nesting indentation
            if nested_indent is None and line.strip():
                nested_indent = indent
    
    # Process the last key-value pair
    if key is not None:
        if value_lines:
            if nested_indent is not None:
                # Parse nested structure
                nested_lines = [l[nested_indent - base_indent:] for l in value_lines]
                if value_lines[0].lstrip().startswith('- '):
                    result[key] = _parse_yaml_list(nested_lines)
                else:
                    result[key] = _parse_yaml_dict(nested_lines, 0)
            else:
                # Single-line value
                value = value_lines[0].strip()
                result[key] = _convert_value(value)
        else:
            # Empty value
            result[key] = None
    
    return result


def _parse_yaml_list(lines: List[str], base_indent: int = 0) -> List[Any]:
    """
    Parse YAML lines into a list.
    
    Args:
        lines: List of YAML lines
        base_indent: Base indentation level

    Returns:
        Parsed list
    """
    result = []
    item_lines = []
    item_indent = None
    current_indent = None
    
    for line in lines:
        if not line.strip() or line.strip().startswith('#'):
            continue
            
        indent = len(line) - len(line.lstrip())
        
        if indent < base_indent:
            break
            
        if indent == base_indent and line.lstrip().startswith('- '):
            # Process previous item if it exists
            if item_lines:
                if item_indent is not None:
                    # Parse nested structure
                    nested_lines = [l[item_indent - base_indent:] for l in item_lines]
                    if nested_lines[0].lstrip().startswith('- '):
                        result.append(_parse_yaml_list(nested_lines))
                    else:
                        result.append(_parse_yaml_dict(nested_lines, 0))
                else:
                    # Single-line value
                    value = item_lines[0].lstrip()[2:].strip()  # Remove '- '
                    result.append(_convert_value(value))
            
            # Start new item
            item_text = line.lstrip()[2:].strip()  # Remove '- '
            if item_text:
                # Inline item
                result.append(_convert_value(item_text))
                item_lines = []
                item_indent = None
            else:
                # Prepare for multi-line or nested item
                item_lines = []
                item_indent = None
                current_indent = indent
        
        elif item_lines or current_indent is not None:
            if item_indent is None and line.strip():
                item_indent = indent
            item_lines.append(line)
    
    # Process the last item
    if item_lines:
        if item_indent is not None:
            # Parse nested structure
            nested_lines = [l[item_indent - base_indent:] for l in item_lines]
            if nested_lines[0].lstrip().startswith('- '):
                result.append(_parse_yaml_list(nested_lines))
            else:
                result.append(_parse_yaml_dict(nested_lines, 0))
        else:
            # Single-line value
            value = item_lines[0].lstrip()[2:].strip()  # Remove '- '
            result.append(_convert_value(value))
    
    return result


def _convert_value(value: str) -> Any:
    """
    Convert a string value to its appropriate Python type.
    
    Args:
        value: String value to convert

    Returns:
        Converted value in appropriate type
    """
    if not value or value == '~':
        return None
    elif value.lower() == 'true' or value.lower() == 'yes':
        return True
    elif value.lower() == 'false' or value.lower() == 'no':
        return False
    elif value.isdigit():
        return int(value)
    elif re.match(r'^-?\d+$', value):
        return int(value)
    elif re.match(r'^-?\d+\.\d+$', value):
        return float(value)
    elif (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    elif value.startswith('[') and value.endswith(']'):
        items = value[1:-1].split(',')
        return [_convert_value(item.strip()) for item in items]
    else:
        return value


def _dump_yaml(data: Any, indent: int = 2, current_indent: int = 0) -> str:
    """
    Convert Python data to YAML format.
    
    Args:
        data: Data to convert
        indent: Indentation size
        current_indent: Current indentation level

    Returns:
        YAML string
    """
    if data is None:
        return '~'
    elif isinstance(data, bool):
        return 'true' if data else 'false'
    elif isinstance(data, (int, float)):
        return str(data)
    elif isinstance(data, str):
        if re.search(r'[\n:]', data) or data.lower() in ('true', 'false', 'yes', 'no', 'null', 'none', '~'):
            # Quote strings containing newlines, colons, or YAML reserved words
            return f'"{data}"'
        return data
    elif isinstance(data, dict):
        if not data:
            return '{}'
            
        lines = []
        for k, v in data.items():
            spaces = ' ' * current_indent
            if isinstance(v, dict) and v:
                lines.append(f"{spaces}{k}:")
                nested = _dump_yaml(v, indent, current_indent + indent)
                for line in nested.split('\n'):
                    if line:
                        lines.append(f"{' ' * (current_indent + indent)}{line}")
            elif isinstance(v, list) and v:
                lines.append(f"{spaces}{k}:")
                nested = _dump_yaml(v, indent, current_indent + indent)
                for line in nested.split('\n'):
                    if line:
                        lines.append(f"{' ' * (current_indent + indent)}{line}")
            else:
                v_str = _dump_yaml(v, indent, 0)
                lines.append(f"{spaces}{k}: {v_str}")
        return '\n'.join(lines)
    elif isinstance(data, list):
        if not data:
            return '[]'
            
        lines = []
        for item in data:
            spaces = ' ' * current_indent
            if isinstance(item, dict) and item:
                lines.append(f"{spaces}- ")
                nested = _dump_yaml(item, indent, current_indent + indent)
                first = True
                for line in nested.split('\n'):
                    if first:
                        lines[-1] += line
                        first = False
                    else:
                        lines.append(f"{' ' * (current_indent + indent)}{line}")
            elif isinstance(item, list) and item:
                lines.append(f"{spaces}- ")
                nested = _dump_yaml(item, indent, current_indent + indent)
                first = True
                for line in nested.split('\n'):
                    if first:
                        lines[-1] += line
                        first = False
                    else:
                        lines.append(f"{' ' * (current_indent + indent)}{line}")
            else:
                item_str = _dump_yaml(item, indent, 0)
                lines.append(f"{spaces}- {item_str}")
        return '\n'.join(lines)
    else:
        return str(data)