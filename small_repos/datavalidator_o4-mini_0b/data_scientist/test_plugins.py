from schema_validator.schema_validator import Field, SchemaValidator, Plugin

class MultiplyPlugin(Plugin):
    def __init__(self, field_name, factor):
        self.field = field_name
        self.factor = factor
    def process(self, field_name, value):
        if field_name == self.field and value is not None:
            return value * self.factor
        return value

def test_plugin_applied():
    schema = [Field("x", int)]
    validator = SchemaValidator(schema)
    plugin = MultiplyPlugin("x", 10)
    validator.register_plugin(plugin)
    sanitized, errors = validator.validate({"x": 2})
    assert sanitized["x"] == 20
    assert not errors
