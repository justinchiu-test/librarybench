# Ensure full schema output for nested dict
from configschema import ConfigManager, export_json_schema

def test_integration():
    # prepare config manager with nested data
    cm = ConfigManager({"outer": {"inner": 1}, "flag": True})
    schema = export_json_schema(cm.serialize())
    assert "outer" in schema["properties"]
    assert schema["properties"]["outer"]["type"] == "object"
