import os
import sys
import time
import tempfile
import json
import pytest

from mobile_app_dev.config_manager import ConfigManager

def test_setup_logging():
    cm = ConfigManager()
    logger = cm.setup_logging()
    assert hasattr(logger, 'info')
    # calling again should reuse
    logger2 = cm.setup_logging()
    assert logger is logger2

def test_namespace_and_set_get():
    cm = ConfigManager()
    cm._set('global_key', 1)
    assert cm._get('global_key') == 1
    with cm.namespace('prod'):
        cm._set('k', 2)
        assert cm._get('k') == 2
    # outside namespace, global unchanged
    assert cm._get('k') is None
    # config dict has namespace
    cfg = cm._config
    assert 'prod' in cfg and cfg['prod']['k'] == 2

def test_load_yaml(tmp_path, monkeypatch):
    yaml_file = tmp_path / "test.yaml"
    content = "a: 1\nb: hello\n"
    yaml_file.write_text(content)
    cm = ConfigManager()
    # Test loading YAML if available
    try:
        data = cm.load_yaml(str(yaml_file))
        assert data == {'a': 1, 'b': 'hello'}
        assert cm._config['a'] == 1
        assert cm._config['b'] == 'hello'
    except ImportError:
        pytest.skip("yaml library not available")

def test_load_envvars(monkeypatch):
    monkeypatch.setenv('TEST_INT', '10')
    monkeypatch.setenv('TEST_FLOAT', '3.14')
    monkeypatch.setenv('TEST_BOOL', 'true')
    monkeypatch.setenv('OTHER', 'value')
    cm = ConfigManager()
    data = cm.load_envvars(prefix='TEST_')
    assert data['TEST_INT'] == 10
    assert data['TEST_FLOAT'] == 3.14
    assert data['TEST_BOOL'] is True
    assert 'OTHER' not in data

def test_parse_cli_args(monkeypatch):
    cm = ConfigManager()
    monkeypatch.setattr(sys, 'argv', ['prog', '--x=5', '--flag', '--s=hello'])
    data = cm.parse_cli_args()
    assert data['x'] == 5
    assert data['flag'] is True
    assert data['s'] == 'hello'
    assert cm._config['x'] == 5

def test_add_validation_and_validate():
    cm = ConfigManager()
    cm._set('num', 5)
    cm.add_validation_hook('num', min_val=1, max_val=10)
    assert cm.validate()
    cm._set('num', 0)
    with pytest.raises(ValueError):
        cm.validate()
    cm._set('num', 20)
    with pytest.raises(ValueError):
        cm.validate()
    cm._set('url', 'http://test.com')
    cm.add_validation_hook('url', pattern=r'^https?://')
    assert cm.validate()
    cm._set('url', 'ftp://x')
    with pytest.raises(ValueError):
        cm.validate()

def test_export_to_json():
    cm = ConfigManager()
    cm._set('a', 1)
    cm._set('b', 'x')
    js = cm.export_to_json()
    data = json.loads(js)
    assert data['a'] == 1 and data['b'] == 'x'

def test_enable_cache_and_lazy_load():
    cm = ConfigManager()
    calls = {'count':0}
    def loader():
        calls['count'] += 1
        return 'value'
    # enable_cache
    v1 = cm.enable_cache('k', loader)
    v2 = cm.enable_cache('k', loader)
    assert v1 == 'value' and v2 == 'value'
    assert calls['count'] == 1
    # lazy_load
    cm2 = ConfigManager()
    calls2 = {'count':0}
    def loader2():
        calls2['count'] += 1
        return 42
    cm2.lazy_load('heavy', loader2)
    # access property
    assert cm2.heavy == 42
    assert cm2.heavy == 42
    assert calls2['count'] == 1

def test_hot_reload(tmp_path):
    cm = ConfigManager()
    temp = tmp_path / "f.txt"
    temp.write_text("old")
    callback_called = {'flag': False, 'path': None}
    def cb(path):
        callback_called['flag'] = True
        callback_called['path'] = path
    handle = cm.hot_reload(str(temp), cb, interval=0.05)
    # modify file
    time.sleep(0.1)
    temp.write_text("new")
    # wait for callback
    time.sleep(0.2)
    handle.stop()
    assert callback_called['flag'] is True
    assert callback_called['path'] == str(temp)

def test_full_namespace_workflow(tmp_path):
    cm = ConfigManager()
    # default ns
    cm._set('x', 1)
    with cm.namespace('dev'):
        # load yaml into ns
        yaml_file = tmp_path / "ns.yaml"
        yaml_file.write_text("f: foo\n")
        try:
            cm.load_yaml(str(yaml_file))
        except ImportError:
            pass
        cm._set('n', 2)
    # export json
    js = cm.export_to_json()
    data = json.loads(js)
    assert data.get('x') == 1
    if 'dev' in data:
        assert data['dev']['n'] == 2

def test_parse_cli_args_override(monkeypatch):
    cm = ConfigManager()
    cm._set('a', 1)
    monkeypatch.setattr(sys, 'argv', ['prog', '--a=5'])
    data = cm.parse_cli_args()
    assert data['a'] == 5
    assert cm._config['a'] == 5
