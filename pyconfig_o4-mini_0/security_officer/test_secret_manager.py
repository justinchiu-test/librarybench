import pytest
from config_framework.secret_manager import SecretManager

def test_get_and_cache():
    sm = SecretManager()
    first = sm.get_secret("api_key")
    second = sm.get_secret("api_key")
    assert first == second
    assert first == "secret_api_key"

def test_rotate_secret():
    sm = SecretManager()
    old = sm.get_secret("token")
    new = sm.rotate_secret("token")
    assert new != old
    assert new == "secret_token_v2"
    cached = sm.get_secret("token")
    assert cached == new
