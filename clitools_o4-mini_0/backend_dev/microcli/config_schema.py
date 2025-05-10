def gen_config_schema(definition: dict) -> dict:
    # Wrap a simple JSON schema
    return {
        "type": "object",
        "properties": definition,
        "required": list(definition.keys())
    }
