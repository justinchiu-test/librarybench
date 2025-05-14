"""Configuration schema generation for data scientist CLI tools."""

from typing import Dict, Any, Type


def generate_schema(fields: Dict[str, Type]) -> Dict[str, Dict[str, str]]:
    """
    Generate a simple schema from a dictionary of field types.

    Args:
        fields (Dict[str, Type]): Dictionary mapping field names to their Python types.

    Returns:
        Dict[str, Dict[str, str]]: Schema with field types.
    """
    schema = {}

    type_mapping = {
        int: 'integer',
        str: 'string',
        bool: 'boolean',
        list: 'list',
        dict: 'dict',
        float: 'float'
    }

    for field_name, field_type in fields.items():
        schema[field_name] = {
            'type': type_mapping.get(field_type, 'unknown')
        }

    return schema