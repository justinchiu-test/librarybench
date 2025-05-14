TYPE_MAP = {
    str: 'string',
    int: 'integer',
    float: 'number',
    bool: 'boolean',
    dict: 'object',
    list: 'array'
}

def gen_config_schema(definition):
    """
    Build a JSON schema dict from a dict of key:type
    """
    properties = {}
    required = []
    for key, typ in definition.items():
        t = TYPE_MAP.get(typ, 'string')
        properties[key] = {'type': t}
        required.append(key)
    schema = {
        'type': 'object',
        'properties': properties,
        'required': required
    }
    return schema
