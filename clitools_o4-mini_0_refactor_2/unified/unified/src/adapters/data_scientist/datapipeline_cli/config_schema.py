"""
Generate config schema for data_scientist datapipeline CLI.
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
    for k, t in fields.items():
        schema[k] = {'type': type_map.get(t, 'string')}
    return schema