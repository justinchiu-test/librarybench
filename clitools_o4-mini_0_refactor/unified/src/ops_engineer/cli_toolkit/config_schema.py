"""
Generate JSON schema from Python type definitions for ops engineers.
"""
def gen_config_schema(definition):
    type_map = {
        str: 'string',
        int: 'integer',
        bool: 'boolean',
        float: 'number',
        list: 'array',
        dict: 'object',
    }
    properties = {}
    required = []
    for key, pytype in definition.items():
        if pytype not in type_map:
            raise ValueError(f"Unsupported type for key {key}: {pytype}")
        properties[key] = {'type': type_map[pytype]}
        required.append(key)
    return {
        'type': 'object',
        'properties': properties,
        'required': required,
    }