from config_framework.schema import export_schema

def test_export_schema_types():
    config = {
        "name": "app",
        "retries": 3,
        "debug": False,
        "items": [1,2],
        "opts": {"a": 1},
        "pi": 3.14
    }
    schema = export_schema(config)
    props = schema["properties"]
    assert props["name"]["type"] == "string"
    assert props["retries"]["type"] == "integer"
    assert props["debug"]["type"] == "boolean"
    assert props["items"]["type"] == "array"
    assert props["opts"]["type"] == "object"
    assert props["pi"]["type"] == "number"
