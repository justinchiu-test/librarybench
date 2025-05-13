# Ensure full schema output for nested dict
from configmanager import ConfigManager, export_json_schema
def test_integration(tmp_path):
    ConfigManager._config = {"outer": {"inner": 1}, "flag": True}
    schema = export_json_schema(ConfigManager.serialize())
    assert "outer" in schema["properties"]
    assert schema["properties"]["outer"]["type"] == "object"
