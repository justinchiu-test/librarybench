"""
Validate config for data_scientist datapipeline CLI.
"""
def validate_config(config, schema):
    # Check missing keys
    for key in schema:
        if key not in config:
            raise ValueError(f"Missing key: {key}")
    # Type checking
    type_map = {
        'integer': int,
        'string': str,
        'boolean': bool,
    }
    for key, definition in schema.items():
        val = config.get(key)
        t = definition.get('type')
        py_t = type_map.get(t)
        if py_t and not isinstance(val, py_t):
            raise ValueError(f"Type mismatch for {key}")
    return True