from plugin_ext.plugin import Plugin

def test_gdpr_validator_flags_email():
    plugin = Plugin()
    data = {'user': {'email': 'alice@example.com', 'name': 'Alice'}, 'note': 'no email'}
    errors = plugin.gdpr_validator(data)
    assert isinstance(errors, list)
    assert any(e['code'] == 'GDPR001' and 'user.email' in e['path'] for e in errors)
    # No error for note field
    assert all('note' not in e['path'] for e in errors)
