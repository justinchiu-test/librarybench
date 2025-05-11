import os
import time
import threading
import tempfile
import configparser
import pytest
import logging
from ci_qa_engineer.config_manager import ConfigManager, CacheManager, setup_logging

def test_setup_logging():
    logger = setup_logging('test_logger')
    assert logger.name == 'test_logger'
    assert logger.level == 10  # DEBUG

def test_merge_configs_default_override():
    cm = ConfigManager()
    defaults = {'a': 1, 'b': 2}
    flags = {'a': 10}
    env = {'b': 20}
    merged = cm.merge_configs(defaults, flags, env)
    assert merged == {'a': 10, 'b': 20}

def test_merge_configs_with_precedence():
    cm = ConfigManager()
    cm.set_precedence({'x': ['defaults', 'flags', 'env'], 'y': ['env', 'defaults']})
    defaults = {'x': 1, 'y': 1}
    flags = {'x': 2, 'y': 2}
    env = {'x': 3, 'y': 3}
    merged = cm.merge_configs(defaults, flags, env)
    # x prefers defaults so x=1; y prefers env first then defaults so y=3
    assert merged['x'] == 1
    assert merged['y'] == 3

def test_export_env_vars():
    cm = ConfigManager()
    cfg = {'ONE': '1', 'TWO': '2'}
    pairs = cm.export_env_vars(cfg)
    assert sorted(pairs) == sorted(['ONE=1', 'TWO=2'])

def test_export_to_ini(tmp_path):
    cm = ConfigManager()
    cfg = {'key1': 'value1', 'key2': 2}
    ini_path = tmp_path / "out.ini"
    cm.export_to_ini(cfg, str(ini_path))
    parser = configparser.ConfigParser()
    parser.read(str(ini_path))
    assert parser['DEFAULT']['key1'] == 'value1'
    assert parser['DEFAULT']['key2'] == '2'

def test_select_profile():
    cm = ConfigManager()
    base = {'common': True}
    overrides = {'dev': {'debug': True}, 'prod': {'debug': False}}
    configs = list(cm.select_profile(base, overrides))
    assert any(c['profile'] == 'dev' and c['debug'] for c in configs)
    assert any(c['profile'] == 'prod' and not c['debug'] for c in configs)

def test_cache_manager():
    cache = CacheManager()
    calls = []
    def factory():
        calls.append(1)
        return 'result'
    r1 = cache.get('k', factory)
    r2 = cache.get('k', factory)
    assert r1 == 'result'
    assert r2 == 'result'
    assert len(calls) == 1

def test_register_plugin_and_validation(caplog):
    cm = ConfigManager()
    def bad_plugin(cfg):
        if 'fail' in cfg:
            raise ValueError("fail")
        return True
    cm.register_plugin(bad_plugin)
    defaults = {'a': 1}
    flags = {}
    env = {'fail': True}
    caplog.set_level(logging.ERROR)
    merged = cm.merge_configs(defaults, flags, env)
    assert 'fail' in merged
    assert any("exception" in rec.message.lower() or "validation failure" in rec.message.lower() for rec in caplog.records)

def test_fetch_secret():
    cm = ConfigManager()
    src1 = {'a': 1}
    src2 = {'b': 2}
    val = cm.fetch_secret('b', [src1, src2])
    assert val == 2
    missing = cm.fetch_secret('c', [src1])
    assert missing is None

def test_enable_hot_reload(tmp_path):
    cm = ConfigManager()
    file_path = tmp_path / "test.txt"
    file_path.write_text("v1")
    events = []
    def callback(p):
        events.append(p)
    cm.enable_hot_reload([str(file_path)], callback, poll_interval=0.1)
    # modify file
    time.sleep(0.2)
    file_path.write_text("v2")
    # give watcher time to detect
    timeout = time.time() + 2.0
    while time.time() < timeout and not events:
        time.sleep(0.05)
    cm.stop_hot_reload()
    assert events and events[0] == str(file_path)
