"""Configuration validator for operations engineer CLI tools."""

from typing import Dict, Any
from src.cli_core.validation import validate_config as core_validate_config

# Re-export for backward compatibility with parameter order matching test expectations
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
    return core_validate_config(schema, config)