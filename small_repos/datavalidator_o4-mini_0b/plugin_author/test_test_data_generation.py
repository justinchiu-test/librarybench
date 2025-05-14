from plugin_ext.plugin import Plugin

def test_generate_test_data_matches_schema():
    plugin = Plugin()
    schema = {
        'properties': {
            'name': {'type': 'string'},
            'count': {'type': 'integer'},
            'value': {'type': 'number'},
            'other': {'type': 'boolean'}
        }
    }
    sample = plugin.generate_test_data(schema)
    assert sample['name'] == 'test'
    assert sample['count'] == 42
    assert sample['value'] == 3.14
    assert sample['other'] is None
