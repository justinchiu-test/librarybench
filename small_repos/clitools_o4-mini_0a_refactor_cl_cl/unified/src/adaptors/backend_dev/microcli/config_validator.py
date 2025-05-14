"""Adapter for backend_dev.microcli.config_validator."""

from typing import Dict, Any, List, Union, Literal, Optional

def validate_config(config: Dict[str, Any], schema: Dict[str, Any]) -> bool:
    """Validate a configuration against a JSON Schema.

    Args:
        config (Dict): Configuration dictionary
        schema (Dict): JSON Schema validation schema

    Returns:
        bool: True if valid, False if invalid

    Raises:
        ValueError: If schema is not an object schema
    """
    # Check if schema is an object schema
    if schema.get("type") != "object":
        raise ValueError("Only object schemas are supported")

    # Get required fields and properties
    required = schema.get("required", [])
    properties = schema.get("properties", {})

    # Check for missing required fields
    for field in required:
        if field not in config:
            return False

    # Check property types
    for field_name, value in config.items():
        if field_name in properties:
            prop_schema = properties[field_name]

            # Check type
            if "type" in prop_schema:
                schema_type = prop_schema["type"]

                # Simple type validation
                if schema_type == "string" and not isinstance(value, str):
                    return False
                elif schema_type == "number" and not isinstance(value, (int, float)):
                    return False
                elif schema_type == "integer" and not isinstance(value, int):
                    return False
                elif schema_type == "boolean" and not isinstance(value, bool):
                    return False
                elif schema_type == "object" and not isinstance(value, dict):
                    return False
                elif schema_type == "array" and not isinstance(value, list):
                    return False

    # If we got here, validation passed
    return True