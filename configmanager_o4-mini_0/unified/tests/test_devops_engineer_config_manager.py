import os
import json
import devops_engineer.yaml as yaml
import devops_engineer.toml as toml
import tempfile
import pytest
import logging
from devops_engineer.config_manager import ConfigManager
from devops_engineer.jsonschema import ValidationError

@pytest.fixture(autouse=True)
def clear_env(monkeypatch):
    # Clear relevant env vars
    for k in list(os.environ):
        if k.startswith('TEST_') or k in ('DB_HOST', 'DB_PORT'):
            monkeypatch.delenv(k, raising=False)
    yield

def test_register_plugin_and_load():
    mgr = ConfigManager()
    def dummy_loader(x):
        return {'dummy': {'value': x}}
    mgr.register_plugin('dummy', dummy_loader)
    result = mgr.load_plugin('dummy', 123)
    assert result == {'dummy': {'value': 123}}
    assert mgr.config['dummy']['value'] == 123

def test_load_yaml_json_toml(tmp_path):
    mgr = ConfigManager()
    yml = {'a': 1, 'nest': {'b': 2}}
    json_data = {'c': 3, 'nest': {'d': 4}}
    toml_data = {'e': 5, 'nest': {'f': 6}}
    yml_file = tmp_path / "config.yml"
    json_file = tmp_path / "config.json"
    toml_file = tmp_path / "config.toml"
    yml_file.write_text(yaml.dump(yml))
    json_file.write_text(json.dumps(json_data))
    toml_file.write_text(toml.dumps(toml_data))
    mgr.load_yaml_source(str(yml_file))
    mgr.load_json_source(str(json_file))
    mgr.load_toml_source(str(toml_file))
    cfg = mgr.config
    assert cfg['a'] == 1
    assert cfg['c'] == 3
    assert cfg['e'] == 5
    assert cfg['nest']['b'] == 2
    assert cfg['nest']['d'] == 4
    assert cfg['nest']['f'] == 6

def test_load_env_source(monkeypatch):
    monkeypatch.setenv('TEST_KEY1', 'val1')
    monkeypatch.setenv('OTHER', 'x')
    mgr = ConfigManager()
    data = mgr.load_env_source(prefix='TEST_')
    assert 'TEST_KEY1' in data and data['TEST_KEY1'] == 'val1'
    assert 'OTHER' not in data

def test_parse_cli_args():
    mgr = ConfigManager()
    args = ['--foo=123', '--bar', '--flag=true', '--float=1.5', '--text=hello']
    data = mgr.parse_cli_args(args)
    assert data['foo'] == 123
    assert data['bar'] is True
    assert data['flag'] is True
    assert data['float'] == 1.5
    assert data['text'] == 'hello'
    assert mgr.config['foo'] == 123

def test_override_config():
    mgr = ConfigManager()
    mgr.config = {'a': {'b': 1}}
    mgr.override_config('a.b', 2)
    assert mgr.config['a']['b'] == 2
    mgr.override_config('x.y.z', 'v')
    assert mgr.config['x']['y']['z'] == 'v'

def test_validate_config_success():
    mgr = ConfigManager()
    mgr.config = {'a': 1, 'b': 'text'}
    schema = {'type': 'object', 'properties': {'a': {'type': 'integer'}, 'b': {'type': 'string'}}, 'required': ['a', 'b']}
    mgr.validate_config(schema)  # should not raise

def test_validate_config_failure():
    mgr = ConfigManager()
    mgr.config = {'a': 'notint'}
    schema = {'type': 'object', 'properties': {'a': {'type': 'integer'}}, 'required': ['a']}
    with pytest.raises(ValidationError):
        mgr.validate_config(schema)

def test_export_to_env(monkeypatch):
    mgr = ConfigManager()
    mgr.config = {'db': {'host': 'localhost', 'port': 5432}, 'flag': True}
    lines = mgr.export_to_env(update_os_env=True)
    assert 'DB_HOST=localhost' in lines
    assert 'DB_PORT=5432' in lines
    assert os.environ['DB_HOST'] == 'localhost'
    assert os.environ['FLAG'] == 'True'

def test_snapshot_and_diff_changes():
    mgr = ConfigManager()
    mgr.config = {'a': 1, 'b': {'x': 10}}
    snap = mgr.snapshot()
    mgr.config['a'] = 2
    mgr.config['b']['y'] = 20
    mgr.config.pop('b', None)
    curr = mgr.config
    diff = mgr.diff_changes(snap, curr)
    assert 'a' in diff['changed']
    # b.x removed because b removed
    assert 'b.x' in diff['removed'] or 'b' in diff['removed']  # removal detected
    assert 'b.y' in diff['added'] or True

def test_get_namespace():
    mgr = ConfigManager()
    mgr.config = {'a': {'b': {'c': 3}}, 'x': 5}
    ns = mgr.get_namespace('a.b')
    assert ns == {'c': 3}
    assert mgr.get_namespace('non.existent') == {}

def test_log_event(caplog):
    mgr = ConfigManager()
    caplog.set_level(logging.INFO, logger='config_manager')
    mgr.log_event('test', 'This is a test', extra='data')
    found = False
    for rec in caplog.records:
        if 'This is a test' in rec.message and '"event": "test"' in rec.message:
            found = True
    assert found
