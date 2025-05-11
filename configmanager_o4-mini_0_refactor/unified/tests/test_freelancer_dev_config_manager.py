import os
import json
import time
import threading
import logging
import tempfile
import configparser
import pytest
from freelancer_dev.config_manager import ConfigManager

class DummySecretStore:
    def __init__(self):
        self.store = {'secret1': 'value1'}
    def get(self, name):
        return self.store.get(name)

class DummyMergePlugin:
    def __init__(self, data):
        self.data = data
    def merge(self):
        return self.data

def test_merge_configs_default_file_env(tmp_path, monkeypatch):
    defaults = {'a': 1, 'nested': {'x': 10}}
    file_cfg = {'b': 2, 'nested': {'y': 20}}
    file_path = tmp_path / "cfg.json"
    file_path.write_text(json.dumps(file_cfg))
    monkeypatch.setenv('a', '100')
    cm = ConfigManager(defaults=defaults, file_path=str(file_path))
    merged = cm.merge_configs()
    assert merged['a'] == '100'
    assert merged['b'] == 2
    assert merged['nested']['x'] == 10
    assert merged['nested']['y'] == 20

def test_set_precedence(monkeypatch, tmp_path):
    defaults = {'k': 1}
    file_cfg = {'k': 2}
    monkeypatch.setenv('k', '3')
    file_path = tmp_path / "cfg.json"
    file_path.write_text(json.dumps(file_cfg))
    cm = ConfigManager(defaults=defaults, file_path=str(file_path))
    cm.set_precedence(['env', 'file', 'defaults'])
    merged = cm.merge_configs()
    assert merged['k'] == '3'

def test_select_profile(tmp_path):
    defaults = {'profiles': {'dev': {'db': 'sqlite'}, 'prod': {'db': 'postgres'}}}
    cm = ConfigManager(defaults=defaults)
    prof = cm.select_profile('dev')
    assert prof == {'db': 'sqlite'}
    with pytest.raises(KeyError):
        cm.select_profile('missing')

def test_export_env_vars(monkeypatch):
    defaults = {'x': '1', 'y': '2'}
    monkeypatch.setenv('y', '20')
    cm = ConfigManager(defaults=defaults)
    lines = cm.export_env_vars()
    assert 'x=1' in lines and 'y=20' in lines
    # test to_os
    os.environ.pop('x', None)
    cm.export_env_vars(to_os=True)
    assert os.environ.get('x') == '1'

def test_export_to_ini(tmp_path):
    defaults = {'a': '1', 'section': {'b': '2'}}
    cm = ConfigManager(defaults=defaults)
    ini_str = cm.export_to_ini()
    assert '[section]' in ini_str
    assert 'b = 2' in ini_str or 'b=2' in ini_str
    # test file output
    ini_file = tmp_path / "out.ini"
    cm.export_to_ini(file_path=str(ini_file))
    cp = configparser.ConfigParser()
    cp.read(str(ini_file))
    assert cp.get('DEFAULT', 'a') == '1'
    assert cp.get('section', 'b') == '2'

def test_hot_reload(tmp_path):
    data1 = {'val': 1}
    data2 = {'val': 2}
    file_path = tmp_path / "hot.json"
    file_path.write_text(json.dumps(data1))
    cm = ConfigManager(file_path=str(file_path))
    callback_called = threading.Event()
    def cb():
        callback_called.set()
    cm.enable_hot_reload(interval=0.1, callback=cb)
    time.sleep(0.2)
    file_path.write_text(json.dumps(data2))
    time.sleep(0.3)
    cm.disable_hot_reload()
    assert callback_called.is_set()
    # verify file_config updated
    assert cm.file_config['val'] == 2

def test_setup_logging(tmp_path, caplog):
    log_file = tmp_path / "log.txt"
    cm = ConfigManager()
    cm.setup_logging(log_file=str(log_file), level=logging.DEBUG)
    cm.logger.debug("debug message")
    cm.logger.info("info message")
    # check file
    time.sleep(0.1)
    with open(log_file, 'r') as f:
        content = f.read()
    assert "debug message" in content
    assert "info message" in content

def test_fetch_secret_and_register_plugin():
    cm = ConfigManager()
    dummy = DummySecretStore()
    cm.register_plugin('default', dummy)
    val = cm.fetch_secret('secret1')
    assert val == 'value1'
    with pytest.raises(KeyError):
        cm.fetch_secret('x', store='missing')

def test_cache_manager():
    cm = ConfigManager()
    calls = {'count': 0}
    @cm.cache_manager
    def compute(x):
        calls['count'] += 1
        return x * x
    res1 = compute(3)
    res2 = compute(3)
    assert res1 == 9 and res2 == 9
    assert calls['count'] == 1

def test_register_plugin_merge():
    defaults = {'a': 1}
    plugin_data = {'b': 2}
    cm = ConfigManager(defaults=defaults)
    plugin = DummyMergePlugin(plugin_data)
    cm.register_plugin('custom', plugin)
    cm.set_precedence(['defaults', 'custom'])
    merged = cm.merge_configs()
    assert merged['a'] == 1
    assert merged['b'] == 2
