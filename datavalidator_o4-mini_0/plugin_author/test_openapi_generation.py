from plugin_ext.plugin import Plugin

def test_augment_schema_adds_metadata():
    plugin = Plugin()
    schema = {'type': 'object'}
    updated = plugin.augment_schema(schema.copy())
    assert 'x-plugin-metadata' in updated
    assert updated['x-plugin-metadata']['info'] == 'plugin_ext'
