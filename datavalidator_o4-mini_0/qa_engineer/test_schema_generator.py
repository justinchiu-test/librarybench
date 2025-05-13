import json
from schema_generator import generate_json_schema

def test_schema_generator():
    schema = {'type': 'object'}
    js = generate_json_schema(schema)
    assert json.loads(js) == schema
