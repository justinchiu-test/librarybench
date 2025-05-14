from plugin_ext.plugin import Plugin

def test_apply_aliases_transforms_keys():
    plugin = Plugin()
    plugin.aliases = {'fname': 'first_name', 'lname': 'last_name'}
    data = {'fname': 'John', 'age': 25, 'lname': 'Doe'}
    result = plugin.apply_aliases(data)
    assert 'first_name' in result and result['first_name'] == 'John'
    assert 'last_name' in result and result['last_name'] == 'Doe'
    assert 'age' in result and result['age'] == 25
