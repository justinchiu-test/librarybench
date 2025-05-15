def validate_config(config: dict, schema: dict) -> bool:
    if schema.get("type") != "object":
        raise ValueError("Unsupported schema type")
    props = schema.get("properties", {})
    req = schema.get("required", [])
    for key in req:
        if key not in config:
            return False
        # type checking
        expected = props.get(key, {}).get("type")
        if expected and not isinstance(config[key], {"string": str, "number": (int, float), "object": dict}.get(expected, object)):
            return False
    return True
