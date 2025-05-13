import pytest
from plugin_framework.secure_input import secure_input

def test_secure_input(monkeypatch):
    monkeypatch.setattr('getpass.getpass', lambda prompt: 'secret')
    val = secure_input('Enter:')
    assert val == 'secret'
