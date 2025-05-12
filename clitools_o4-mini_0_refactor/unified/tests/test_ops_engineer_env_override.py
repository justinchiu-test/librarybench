import os
from ops_engineer.cli_toolkit.env_override import env_override

def test_env_override(monkeypatch):
    cfg = {'host': 'localhost', 'port': 8080}
    monkeypatch.setenv('APPHOST', '1.2.3.4')
    monkeypatch.setenv('APPPORT', '9090')
    out = env_override(cfg, 'app')
    assert out['host'] == '1.2.3.4'
    assert out['port'] == '9090'

def test_no_override(monkeypatch):
    cfg = {'a': 'b'}
    out = env_override(cfg, 'X_')
    assert out == cfg
