import os
import sys
import tempfile
import logging
import pytest
from config_manager import (
    register_plugin, plugin_registry, validate_config, export_to_env,
    get_namespace, snapshot, load_toml_source, diff_changes,
    override_config, parse_cli_args, log_event
)

def test_register_plugin_and_conflict():
    plugin_registry.clear()
    def loader(): pass
    register_plugin('test', loader)
    assert 'test' in plugin_registry
    with pytest.raises(KeyError):
        register_plugin('test', loader)
    with pytest.raises(ValueError):
        register_plugin('new', "not_callable")

def test_validate_config_success_and_failure(caplog):
    config = {'a': 1, 'b': 'x'}
    schema = {
        'required': ['a', 'b'],
        'properties': {'a': {'type': 'integer'}, 'b': {'type': 'string'}}
    }
    caplog.set_level(logging.INFO)
    assert validate_config(config, schema) is True
    assert any('validation_success' in rec.message for rec in caplog.records)
    bad = {'a': 'not_int'}
    with pytest.raises(ValueError):
        validate_config(bad, schema)
    bad2 = {'a': 'not_int', 'b': 'x'}
    with pytest.raises(TypeError):
        validate_config(bad2, schema)

def test_export_to_env(tmp_path, monkeypatch):
    cfg = {'one': 1, 'nested': {'two': 'b'}}
    monkeypatch.delenv('ONE', raising=False)
    monkeypatch.delenv('NESTED_TWO', raising=False)
    lines = export_to_env(cfg, inject=True)
    assert 'ONE=1' in lines and 'NESTED_TWO=b' in lines
    assert os.environ['ONE'] == '1'
    assert os.environ['NESTED_TWO'] == 'b'
    # test without inject
    monkeypatch.delenv('ONE', raising=False)
    lines2 = export_to_env(cfg, inject=False)
    assert 'ONE=1' in lines2
    assert 'ONE' not in os.environ

def test_get_namespace_and_error():
    cfg = {'model': {'layers': 3}}
    assert get_namespace(cfg, 'model.layers') == 3
    with pytest.raises(KeyError):
        get_namespace(cfg, 'model.missing')

def test_snapshot_independence():
    cfg = {'a': {'b': 2}}
    snap = snapshot(cfg)
    cfg['a']['b'] = 5
    assert snap['a']['b'] == 2

def test_load_toml_source(tmp_path):
    content = "title = 'Test'\n[x]\ny = 10\n"
    file = tmp_path / "cfg.toml"
    file.write_text(content)
    loaded = load_toml_source(str(file))
    assert loaded['title'] == 'Test'
    assert loaded['x']['y'] == 10

def test_diff_changes():
    old = {'a': 1, 'b': {'c': 2}}
    new = {'a': 1, 'b': {'c': 3}, 'd': 4}
    diffs = diff_changes(old, new)
    assert diffs == {'b.c': (2, 3), 'd': (None, 4)}

def test_override_config():
    cfg = {'a': 1, 'b': {'c': 2}}
    result = override_config(cfg, {'a': 5, 'b': {'c': 3, 'd': 4}})
    assert result['a'] == 5
    assert result['b']['c'] == 3
    assert result['b']['d'] == 4

def test_parse_cli_args(monkeypatch):
    monkeypatch.setattr(sys, 'argv', ['prog', '--lr=0.01', '--batch-size', '32', '--flag=true'])
    overrides = parse_cli_args()
    assert overrides['lr'] == 0.01
    assert overrides['batch_size'] == 32
    assert overrides['flag'] is True

def test_log_event(caplog):
    caplog.set_level(logging.INFO)
    log_event('test_event', 'hello')
    assert any('test_event:hello' in rec.message for rec in caplog.records)
