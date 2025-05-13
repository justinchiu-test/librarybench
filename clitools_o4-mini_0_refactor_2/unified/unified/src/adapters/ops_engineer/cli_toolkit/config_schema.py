"""
Generate JSON schema from Python type definitions for Operations Engineer CLI.
"""
def gen_config_schema(defs):
    type_map = {str: 'string', int: 'integer', bool: 'boolean', float: 'number', list: 'array', dict: 'object'}
    properties = {}
    for key, t in defs.items():
        properties[key] = {'type': type_map.get(t, 'string')}
    return {'type': 'object', 'properties': properties, 'required': list(defs.keys())}