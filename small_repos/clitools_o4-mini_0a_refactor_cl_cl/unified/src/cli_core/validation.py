"""
Configuration validation for CLI tools.

This module provides utilities for validating configuration against JSON schema.
"""

from typing import Dict, Any, Optional, List, Union


def validate_config(schema: Dict[str, Any], config: Dict[str, Any]) -> bool:
    """
    Validate a configuration against a schema.

    Args:
        schema (Dict[str, Any]): Schema to validate against.
        config (Dict[str, Any]): Configuration to validate.

    Returns:
        bool: True if the configuration is valid.

    Raises:
        ValueError: If the configuration doesn't match the schema.
    """
    type_checkers = {
        'integer': lambda x: isinstance(x, int),
        'string': lambda x: isinstance(x, str),
        'boolean': lambda x: isinstance(x, bool),
        'array': lambda x: isinstance(x, list),
        'object': lambda x: isinstance(x, dict),
        'number': lambda x: isinstance(x, (int, float))
    }

    # Check schema type
    if schema.get('type') == 'object':
        properties = schema.get('properties', {})
        required = schema.get('required', [])

        # Check required fields
        for key in required:
            if key not in config:
                raise ValueError(f"Missing required key: {key}")

        # Validate properties
        for prop_name, prop_schema in properties.items():
            if prop_name in config:
                prop_value = config[prop_name]
                prop_type = prop_schema.get('type')

                # Type validation
                checker = type_checkers.get(prop_type)
                if checker and not checker(prop_value):
                    raise ValueError(
                        f"Invalid type for {prop_name}: expected {prop_type}, got {type(prop_value).__name__}"
                    )

                # Nested object validation
                if prop_type == 'object' and 'properties' in prop_schema:
                    validate_config(prop_schema, prop_value)

                # Array validation
                if prop_type == 'array' and 'items' in prop_schema and isinstance(prop_value, list):
                    item_schema = prop_schema['items']
                    for i, item in enumerate(prop_value):
                        if item_schema.get('type') == 'object':
                            validate_config(item_schema, item)
                        else:
                            # Simple type check for array items
                            item_type = item_schema.get('type')
                            checker = type_checkers.get(item_type)
                            if checker and not checker(item):
                                raise ValueError(
                                    f"Invalid type for item {i} in {prop_name}: expected {item_type}, got {type(item).__name__}"
                                )

    return True