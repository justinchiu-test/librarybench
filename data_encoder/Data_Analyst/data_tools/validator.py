def validate(data, schema):
    """
    Validate the data against the provided schema.
    Schema format:
    - Primitive: {'type': 'int'/'float'/'str'/'bool'}
    - List: {'type': 'list', 'schema': <element schema>}
    - Dict: {'type': 'dict', 'schema': {key1: <schema1>, ...}}
    Returns True if data conforms to schema, False otherwise.
    """
    expected_type = schema.get('type')
    if expected_type in ('int', 'float', 'str', 'bool'):
        if expected_type == 'int':
            return isinstance(data, int) and not isinstance(data, bool)
        if expected_type == 'float':
            return isinstance(data, float)
        if expected_type == 'str':
            return isinstance(data, str)
        if expected_type == 'bool':
            return isinstance(data, bool)
    elif expected_type == 'list':
        if not isinstance(data, list):
            return False
        elem_schema = schema.get('schema')
        if elem_schema is None:
            return False
        for item in data:
            if not validate(item, elem_schema):
                return False
        return True
    elif expected_type == 'dict':
        if not isinstance(data, dict):
            return False
        dict_schema = schema.get('schema')
        if not isinstance(dict_schema, dict):
            return False
        for key, subschema in dict_schema.items():
            if key not in data:
                return False
            if not validate(data[key], subschema):
                return False
        return True
    else:
        return False
