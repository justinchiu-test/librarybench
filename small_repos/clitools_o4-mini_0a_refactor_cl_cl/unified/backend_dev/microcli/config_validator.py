"""Configuration validator for backend developer CLI tools."""

def validate_config(config, schema):
    """Validate a configuration against a schema."""
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