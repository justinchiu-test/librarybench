import pytest
from config_manager.secret_manager import SecretManager

class DummyClient:
    def __init__(self):
        self.store = {"a": "1"}
    def read(self, path):
        return self.store.get(path)
    def rotate(self, path):
        val = self.store.get(path)
        new = val + "_cli"
        self.store[path] = new
        return new

def test_get_set_and_rotate_fallback():
    sm = SecretManager()
    sm.set_secret("foo", "bar")
    assert sm.get_secret("foo") == "bar"
    new = sm.rotate_secret("foo")
    assert new == "bar_rotated"
    assert sm.get_secret("foo") == "bar_rotated"

def test_client_integration():
    client = DummyClient()
    sm = SecretManager(client=client)
    assert sm.get_secret("a") == "1"
    r = sm.rotate_secret("a")
    assert r == "1_cli"
    assert sm.get_secret("a") == "1_cli"
