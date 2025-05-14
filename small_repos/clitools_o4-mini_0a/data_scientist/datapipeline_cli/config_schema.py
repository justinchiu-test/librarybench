def generate_schema(fields):
    type_map = {
        int: 'integer',
        float: 'float',
        str: 'string',
        bool: 'boolean',
        list: 'list',
        dict: 'dict'
    }
    schema = {}
    for key, tp in fields.items():
        schema[key] = {'type': type_map.get(tp, 'string')}
    return schema
