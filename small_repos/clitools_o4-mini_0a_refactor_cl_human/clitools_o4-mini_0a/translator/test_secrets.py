import os
import pytest
from secrets import get_secret

def test_get_secret_default_and_env(tmp_path, monkeypatch):
    monkeypatch.delenv('MYKEY', raising=False)
    assert get_secret('MYKEY', default='def') == 'def'
    monkeypatch.setenv('MYKEY', 'val123')
    assert get_secret('MYKEY') == 'val123'
