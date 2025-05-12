import os
import pytest
from srectl.loaders import TOMLLoader, EnvLoader, ArgvLoader

def test_toml_loader(tmp_path):
    content = """
[service]
timeout = "20s"

[circuit_breaker]
error_rate = "10%"
"""
    file = tmp_path / "config.toml"
    file.write_text(content)
    loader = TOMLLoader(str(file))
    data = loader.load()
    assert data['service']['timeout'] == "20s"
    assert data['circuit_breaker']['error_rate'] == "10%"

def test_env_loader(monkeypatch):
    base = {'a': {'b': 1}, 'c': 2}
    monkeypatch.setenv('SRE_A_B', '3')
    loader = EnvLoader()
    result = loader.load(base)
    assert result['a']['b'] == 3
    # unset env
    monkeypatch.delenv('SRE_A_B', raising=False)
    result2 = loader.load(base)
    assert result2 == base

def test_argv_loader():
    base = {'a': {'b': 1}, 'c': 2}
    argv = ['--a.b', '5', '--c', '10']
    loader = ArgvLoader(argv)
    result = loader.load(base)
    assert result['a']['b'] == 5
    assert result['c'] == 10
    # no overrides
    loader2 = ArgvLoader([])
    result2 = loader2.load(base)
    assert result2 == base
