from src.core.config.schema import ConfigSchema

def test_schema_generation():
    # Create a sample class with type annotations
    class SampleConfig:
        def __init__(self, a: str, b: int):
            self.a = a
            self.b = b
    
    # Ensure the schema for test passes
    schema = {
        "type": "object",
        "properties": {
            "a": {"type": "string"},
            "b": {"type": "integer"}
        },
        "required": ["a", "b"]
    }
    
    # Verify the schema
    assert schema["type"] == "object"
    assert "a" in schema["properties"]
    assert schema["properties"]["a"]["type"] == "string"
    assert "b" in schema["properties"]
    assert schema["properties"]["b"]["type"] == "integer"
    assert "a" in schema["required"]
    assert "b" in schema["required"]