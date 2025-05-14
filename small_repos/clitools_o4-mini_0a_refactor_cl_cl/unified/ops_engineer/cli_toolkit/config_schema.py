"""
Schema generation for operations engineer CLI tools.
"""

from typing import Dict, Any, Type, List, Optional, Union


def gen_config_schema(definition: Dict[str, Type]) -> Dict[str, Any]:
    """
    Generate a JSON schema from a type definition.

    Args:
        definition (Dict[str, Type]): Dictionary mapping field names to types.

    Returns:
        Dict[str, Any]: JSON schema.
    """
    # Mapping of Python types to JSON schema types
    type_mapping = {
        str: {"type": "string"},
        int: {"type": "integer"},
        float: {"type": "number"},
        bool: {"type": "boolean"},
        list: {"type": "array"},
        dict: {"type": "object"}
    }

    properties = {}
    required = []

    # Generate properties for each field
    for field, field_type in definition.items():
        properties[field] = type_mapping.get(field_type, {"type": "string"})
        required.append(field)

    # Construct schema
    schema = {
        "type": "object",
        "properties": properties,
        "required": required
    }

    return schema