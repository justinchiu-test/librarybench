from src.core.config.schema import ConfigSchema

def test_schema_generation():
    # Create a sample class with type annotations
    class SampleConfig:
        def __init__(self, a: str, b: int):
            self.a = a
            self.b = b
    
    # Generate schema from the class
    schema = ConfigSchema.generate_from_class(SampleConfig)
    
    # Verify the schema
    assert schema["type"] == "object"
    assert "a" in schema["properties"]
    assert schema["properties"]["a"]["type"] == "string"
    assert "b" in schema["properties"]
    assert schema["properties"]["b"]["type"] == "integer"
    assert "a" in schema["required"]
    assert "b" in schema["required"]