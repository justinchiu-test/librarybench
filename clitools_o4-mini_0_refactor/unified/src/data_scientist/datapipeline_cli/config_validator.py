"""
Validate configs for data scientists.
"""
"""
Validate configurations against simple schema for data scientists.
"""
def validate_config(config, schema):
    # config: dict of values; schema: dict of {key: {'type': type_str}}
    for key, props in schema.items():
        if key not in config:
            raise ValueError(f"Missing key: {key}")
        expected = props.get('type')
        val = config.get(key)
        if expected == 'integer':
            if not isinstance(val, int):
                raise ValueError(f"Invalid type for key {key}: expected integer")
        elif expected == 'string':
            if not isinstance(val, str):
                raise ValueError(f"Invalid type for key {key}: expected string")
        elif expected == 'boolean':
            if not isinstance(val, bool):
                raise ValueError(f"Invalid type for key {key}: expected boolean")
        elif expected == 'list':
            if not isinstance(val, list):
                raise ValueError(f"Invalid type for key {key}: expected list")
        elif expected == 'dict':
            if not isinstance(val, dict):
                raise ValueError(f"Invalid type for key {key}: expected dict")
        elif expected == 'float':
            if not isinstance(val, float):
                raise ValueError(f"Invalid type for key {key}: expected float")
        else:
            raise ValueError(f"Unsupported type for key {key}: {expected}")
    return True