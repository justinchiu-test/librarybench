"""
Validate configurations against JSON schema for Operations Engineer CLI.
"""
def validate_config(schema, data):
    if schema.get('type') != 'object':
        raise ValueError('Schema must be object')
    required = schema.get('required', [])
    props = schema.get('properties', {})
    for key in required:
        if key not in data:
            raise ValueError(f"Missing key: {key}")
    for key, definition in props.items():
        if key in data:
            t = definition.get('type')
            val = data[key]
            if t == 'string' and not isinstance(val, str):
                raise ValueError(f"Invalid type for {key}")
            if t == 'integer' and not isinstance(val, int):
                raise ValueError(f"Invalid type for {key}")
    return True