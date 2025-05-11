import os
import json
import tempfile
import logging
import pytest
from iot_engineer.config_manager import (
    register_plugin, plugins,
    validate_config, ConfigValidationError,
    export_to_env, get_namespace,
    snapshot, get_snapshot,
    load_toml_source, diff_changes,
    override_config, parse_cli_args,
    log_event
)

def test_register_plugin():
    def loader(): pass
    register_plugin('test', loader)
    assert 'test' in plugins
    assert plugins['test'] is loader

def test_validate_config_success():
    cfg = {'a': 1, 'b': {'c': 'hello'}}
    schema = {'a': 'int', 'b': {'c': 'str'}}
    assert validate_config(cfg, schema) is True

def test_validate_config_failure():
    cfg = {'a': '1', 'b': {}}
    schema = {'a': 'int', 'b': {'c': 'str'}}
    with pytest.raises(ConfigValidationError) as exc:
        validate_config(cfg, schema)
    errs = exc.value.errors
    assert any('Expected int at a' in e for e in errs)
    assert any('Missing key: b.c' in e for e in errs)

def test_export_to_env(tmp_path, monkeypatch):
    cfg = {'a': 1, 'b': {'c': 'd'}}
    monkeypatch.delenv('A', raising=False)
    lines = export_to_env(cfg)
    assert "export A='1'" in lines
    assert os.environ['A'] == '1'
    assert "export B_C='d'" in lines
    assert os.environ['B_C'] == 'd'

def test_log_event(caplog):
    caplog.set_level(logging.INFO)
    log_event('test_event', 'this is a message', data={'x': 1})
    records = [json.loads(r.getMessage()) for r in caplog.records]
    assert any(r['event']=='test_event' and r['message']=='this is a message' for r in records)

def test_get_namespace():
    cfg = {'network': {'wifi': {'ssid': 'x', 'pwd': 'y'}}, 'other': 1}
    sub = get_namespace(cfg, 'network.wifi')
    assert sub == {'ssid': 'x', 'pwd': 'y'}
    assert get_namespace(cfg, 'network.eth') == {}

def test_snapshot_and_get_snapshot():
    cfg = {'a': 1}
    sid = snapshot(cfg)
    cfg['a'] = 2
    snap = get_snapshot(sid)
    assert snap == {'a': 1}
    assert cfg['a'] == 2

def test_load_toml_source(tmp_path):
    base = {'a': 1, 'nested': {'x': 5}}
    content = "[nested]\nx = 10\ny = 20\nz = {subkey = 'val'}\nnew = 'yes'\n"
    f = tmp_path / "test.toml"
    f.write_text(content)
    merged = load_toml_source(str(f), base)
    assert merged['a'] == 1
    assert merged['nested']['x'] == 10
    assert merged['nested']['y'] == 20
    assert merged['nested']['z']['subkey'] == 'val'
    assert merged['nested']['new'] == 'yes'

def test_diff_changes():
    old = {'a': 1, 'b': {'x': 10}, 'c': 3}
    new = {'a': 1, 'b': {'x': 20, 'y': 30}, 'd': 4}
    d = diff_changes(old, new)
    assert d['added'] == {'b.y': 30, 'd': 4}
    assert d['removed'] == {'c': 3}
    assert d['changed'] == {'b.x': {'old': 10, 'new': 20}}

def test_override_config():
    cfg = {'a': 1, 'b': {'x': 10, 'y': 20}}
    over = {'b': {'x': 100}, 'c': 3}
    merged = override_config(cfg, over)
    assert merged['a'] == 1
    assert merged['b']['x'] == 100 and merged['b']['y'] == 20
    assert merged['c'] == 3
    # original untouched
    assert cfg['b']['x'] == 10

def test_parse_cli_args():
    args = ['--debug', '--simulate-gps']
    res = parse_cli_args(args)
    assert res['debug'] is True
    assert res['simulate_gps'] is True
