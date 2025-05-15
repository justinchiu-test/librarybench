import json
from configschema import export_json_schema
def test_export_schema():
    cfg = {"a":1,"b":"s","c":[{"d": True}]}
    schema = export_json_schema(cfg)
    assert schema["type"] == "object"
    assert "a" in schema["properties"]
    assert schema["properties"]["a"]["type"] == "integer"
    assert schema["properties"]["c"]["type"] == "array"
