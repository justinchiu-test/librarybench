from ops_engineer.cli_toolkit.config_schema import gen_config_schema

def test_gen_schema_basic():
    definition = {"host": str, "port": int, "debug": bool}
    schema = gen_config_schema(definition)
    assert schema["type"] == "object"
    assert "host" in schema["properties"]
    assert schema["properties"]["port"]["type"] == "integer"
    assert set(schema["required"]) == set(definition.keys())
