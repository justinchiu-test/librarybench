"""
Generate config schema for data scientists.
"""
"""
Generate simple schema mapping for data scientists.
"""
def generate_schema(fields):
    type_map = {
        int: 'integer',
        str: 'string',
        bool: 'boolean',
        list: 'list',
        dict: 'dict',
        float: 'float',
    }
    schema = {}
    for key, pytype in fields.items():
        if pytype not in type_map:
            raise ValueError(f"Unsupported type for field {key}: {pytype}")
        schema[key] = {'type': type_map[pytype]}
    return schema