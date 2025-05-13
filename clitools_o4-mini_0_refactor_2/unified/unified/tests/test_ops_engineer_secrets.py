from adapters.ops_engineer.cli_toolkit.secrets import SecretManager

def test_secret_manager_set_get():
    sm = SecretManager()
    sm.set_secret('k', 'v')
    assert sm.get_secret('k') == 'v'

def test_get_nonexistent():
    sm = SecretManager()
    assert sm.get_secret('none') is None