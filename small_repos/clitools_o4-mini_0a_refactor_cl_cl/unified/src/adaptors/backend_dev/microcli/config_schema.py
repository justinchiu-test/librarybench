"""Adapter for backend_dev.microcli.config_schema."""

from typing import Dict, Any, List

def gen_config_schema(config: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Generate a schema from a configuration dictionary.

    Args:
        config (Dict): Configuration dictionary with property definitions

    Returns:
        Dict: JSON Schema object
    """
    schema = {
        "type": "object",
        "properties": {},
        "required": []
    }

    for key, value in config.items():
        if isinstance(value, dict):
            # Assume existing schema elements
            schema["properties"][key] = value
            # If there's a type, assume it's required
            if "type" in value:
                schema["required"].append(key)

    return schema