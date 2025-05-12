from backend_dev.microcli.config_schema import gen_config_schema

def test_schema_generation():
    defs = {"a": {"type": "string"}, "b": {"type": "number"}}
    schema = gen_config_schema(defs)
    assert schema["type"] == "object"
    assert "a" in schema["properties"]
    assert "b" in schema["required"]
