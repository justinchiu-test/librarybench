from plugin_ext.plugin import Plugin

def test_override_optional_fields_marks_nullable():
    plugin = Plugin()
    schema = {
        'properties': {
            'a': {'type': 'string'},
            'b': {'type': 'integer'}
        },
        'required': ['a']
    }
    updated = plugin.override_optional_fields(schema)
    assert 'nullable' not in updated['properties']['a']
    assert updated['properties']['b'].get('nullable', False) is True
