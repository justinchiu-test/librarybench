import pytest
from config_loader.secret_manager import fetch_secret, rotate_secret

def test_fetch_aws_secret():
    assert fetch_secret('aws', 'db') == 'aws_secret_db'

def test_fetch_vault_secret():
    assert fetch_secret('vault', 'api') == 'vault_secret_api'

def test_fetch_unknown_manager():
    with pytest.raises(ValueError):
        fetch_secret('gcp', 'key')

def test_rotate_aws_secret():
    assert rotate_secret('aws', 'db') == 'aws_rotated_db'

def test_rotate_vault_secret():
    assert rotate_secret('vault', 'api') == 'vault_rotated_api'

def test_rotate_unknown_manager():
    with pytest.raises(ValueError):
        rotate_secret('gcp', 'key')
