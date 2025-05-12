import os
import toml
import pytest
from config.loaders import TOMLLoader, EnvLoader, ArgvLoader

def test_toml_loader(tmp_path):
    data = {'a': 1, 'b': {'c': 2}}
    file = tmp_path / 'exp.toml'
    file.write_text(toml.dumps(data))
    loaded = TOMLLoader.load(str(file))
    assert loaded == data

def test_env_loader(monkeypatch):
    monkeypatch.setenv('DS_URL', 'http://example.com')
    monkeypatch.setenv('DS_KEY', 'secret')
    monkeypatch.setenv('OTHER', 'no')
    config = EnvLoader.load()
    assert config['url'] == 'http://example.com'
    assert config['key'] == 'secret'
    assert 'other' not in config

def test_argv_loader():
    schema = {'learning_rate': 0.01, 'model_name': 'resnet'}
    argv = ['--learning_rate', '0.02', '--model_name', 'vgg']
    overrides = ArgvLoader.load(schema, argv)
    assert overrides['learning_rate'] == 0.02
    assert overrides['model_name'] == 'vgg'
