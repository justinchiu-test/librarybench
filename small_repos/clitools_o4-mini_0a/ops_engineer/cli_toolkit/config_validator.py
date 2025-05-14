def validate_config(schema, data):
    """
    Simple validator: checks required keys and type matching.
    Raises ValueError on failure, returns True otherwise.
    """
    props = schema.get('properties', {})
    reqs = schema.get('required', [])
    for key in reqs:
        if key not in data:
            raise ValueError(f"Missing required key: {key}")
    for key, rules in props.items():
        if key in data:
            expected = rules.get('type')
            val = data[key]
            if expected == 'string' and not isinstance(val, str):
                raise ValueError(f"Key {key} expected string")
            if expected == 'integer' and not isinstance(val, int):
                raise ValueError(f"Key {key} expected integer")
            if expected == 'number' and not isinstance(val, (int, float)):
                raise ValueError(f"Key {key} expected number")
            if expected == 'boolean' and not isinstance(val, bool):
                raise ValueError(f"Key {key} expected boolean")
            if expected == 'object' and not isinstance(val, dict):
                raise ValueError(f"Key {key} expected object")
            if expected == 'array' and not isinstance(val, list):
                raise ValueError(f"Key {key} expected array")
    return True
