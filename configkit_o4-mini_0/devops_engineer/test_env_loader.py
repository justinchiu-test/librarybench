import os
from config_framework.env_loader import EnvLoader

def test_load(monkeypatch):
    monkeypatch.setenv('CLUSTER_HOST', 'localhost')
    monkeypatch.setenv('CLUSTER_PORT', '8080')
    monkeypatch.setenv('OTHER', 'ignore')
    loader = EnvLoader()
    cfg = loader.load()
    assert cfg['host'] == 'localhost'
    assert cfg['port'] == '8080'
    assert 'other' not in cfg
