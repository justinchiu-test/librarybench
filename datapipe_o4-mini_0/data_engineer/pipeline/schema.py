def validate_schema(data, schema):
    if not isinstance(data, dict):
        raise ValueError("Data must be a dict")
    required = schema.get('required', [])
    for key in required:
        if key not in data:
            raise ValueError(f"Missing required field: {key}")
    properties = schema.get('properties', {})
    for key, rules in properties.items():
        if key in data:
            typ = rules.get('type')
            val = data[key]
            if typ == 'string' and not isinstance(val, str):
                raise ValueError(f"Field {key} must be string")
            if typ == 'number' and not isinstance(val, (int, float)):
                raise ValueError(f"Field {key} must be number")
            if typ == 'integer' and not isinstance(val, int):
                raise ValueError(f"Field {key} must be integer")
            if typ == 'boolean' and not isinstance(val, bool):
                raise ValueError(f"Field {key} must be boolean")
            if typ == 'object' and not isinstance(val, dict):
                raise ValueError(f"Field {key} must be object")
            if typ == 'array' and not isinstance(val, list):
                raise ValueError(f"Field {key} must be array")
    custom = schema.get('custom')
    if custom:
        result = custom(data)
        if not result:
            raise ValueError("Custom validation failed")
    return True
