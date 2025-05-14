def validate_config(config, schema):
    for key, rules in schema.items():
        if key not in config:
            raise ValueError(f'Missing key: {key}')
        expected = rules.get('type')
        val = config[key]
        if expected == 'integer' and not isinstance(val, int):
            raise ValueError(f'Key {key} expected integer')
        if expected == 'float' and not isinstance(val, float):
            raise ValueError(f'Key {key} expected float')
        if expected == 'string' and not isinstance(val, str):
            raise ValueError(f'Key {key} expected string')
        if expected == 'boolean' and not isinstance(val, bool):
            raise ValueError(f'Key {key} expected boolean')
        if expected == 'list' and not isinstance(val, list):
            raise ValueError(f'Key {key} expected list')
        if expected == 'dict' and not isinstance(val, dict):
            raise ValueError(f'Key {key} expected dict')
    return True
