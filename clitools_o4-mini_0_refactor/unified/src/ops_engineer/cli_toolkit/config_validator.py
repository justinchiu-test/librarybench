"""
Validate config against JSON schema for ops engineers.
"""
def validate_config(schema, data):
    # schema: JSON schema dict; data: dict to validate
    if schema.get('type') != 'object':
        raise ValueError('Unsupported schema type')
    properties = schema.get('properties', {})
    required = schema.get('required', [])
    # check required keys
    for key in required:
        if key not in data:
            raise ValueError(f'Missing key: {key}')
    # type check
    for key, val in data.items():
        if key in properties:
            expected = properties[key].get('type')
            if expected == 'string' and not isinstance(val, str):
                raise ValueError(f'Key {key} expected string')
            if expected == 'integer' and not isinstance(val, int):
                raise ValueError(f'Key {key} expected integer')
            # additional types can be added as needed
    return True