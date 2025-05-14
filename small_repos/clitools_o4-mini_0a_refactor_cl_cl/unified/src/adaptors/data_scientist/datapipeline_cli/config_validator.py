"""Adapter for data_scientist.datapipeline_cli.config_validator."""

from typing import Dict, Any


def validate_config(config: Dict[str, Any], schema: Dict[str, Dict[str, str]]) -> bool:
    """
    Validate a configuration against a schema.

    Args:
        config (Dict[str, Any]): Configuration to validate.
        schema (Dict[str, Dict[str, str]]): Schema to validate against.

    Returns:
        bool: True if the configuration is valid.

    Raises:
        ValueError: If the configuration doesn't match the schema.
    """
    type_checkers = {
        'integer': lambda x: isinstance(x, int),
        'string': lambda x: isinstance(x, str),
        'boolean': lambda x: isinstance(x, bool),
        'list': lambda x: isinstance(x, list),
        'dict': lambda x: isinstance(x, dict),
        'float': lambda x: isinstance(x, float)
    }

    # Check for missing keys
    for key in schema:
        if key not in config:
            raise ValueError(f"Missing required key: {key}")

    # Check types
    for key, value in config.items():
        if key in schema:
            expected_type = schema[key].get('type')
            checker = type_checkers.get(expected_type)

            if checker and not checker(value):
                raise ValueError(f"Invalid type for {key}: expected {expected_type}, got {type(value).__name__}")

    return True

__all__ = ['validate_config']
