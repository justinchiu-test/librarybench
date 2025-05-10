from datapipeline_cli.config_schema import generate_schema

def test_generate_schema_basic():
    fields = {'a': int, 'b': str, 'c': bool, 'd': list, 'e': dict, 'f': float}
    schema = generate_schema(fields)
    assert schema['a']['type'] == 'integer'
    assert schema['b']['type'] == 'string'
    assert schema['c']['type'] == 'boolean'
    assert schema['d']['type'] == 'list'
    assert schema['e']['type'] == 'dict'
    assert schema['f']['type'] == 'float'
