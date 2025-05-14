from plugins import Plugin
from schema_validator import SchemaValidator

class DummyPlugin(Plugin):
    def __init__(self):
        self.pre_called = False
        self.post_called = False
    def pre_validate(self, payload):
        self.pre_called = True
    def post_validate(self, payload, errors):
        self.post_called = True

def test_plugin_system():
    schema = {'type': 'object', 'properties': {}}
    plugin = DummyPlugin()
    validator = SchemaValidator(schema, plugins=[plugin])
    errors = validator.validate({})
    assert plugin.pre_called
    assert plugin.post_called
