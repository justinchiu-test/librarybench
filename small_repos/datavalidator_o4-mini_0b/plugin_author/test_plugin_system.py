import pytest
from plugin_ext.plugin import Plugin

class DummyHost:
    def __init__(self):
        self.strict_mode = True
        self.hooks = {}
        self.error_reporters = []
        self.schema_augmenters = []
        self.data_generators = []
        self.validators = []

    def register_hook(self, name, fn):
        self.hooks[name] = fn

    def register_error_reporter(self, fn):
        self.error_reporters.append(fn)

    def schema_augmenter(self, fn):
        self.schema_augmenters.append(fn)

    def data_generator(self, fn):
        self.data_generators.append(fn)

def test_register_sets_strict_mode_and_hooks():
    plugin = Plugin()
    host = DummyHost()
    plugin.register(host)
    assert plugin.strict_mode is True
    assert 'coerce' in host.hooks
    assert 'override_optional_fields' in host.hooks
    assert plugin.report_error in host.error_reporters
    assert plugin.augment_schema in host.schema_augmenters
    assert plugin.generate_test_data in host.data_generators
    assert host.logging_namespace == 'plugin_ext'
    assert plugin.gdpr_validator in host.validators
