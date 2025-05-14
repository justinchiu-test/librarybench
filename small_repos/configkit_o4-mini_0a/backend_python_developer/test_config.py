import os
import sys
import time
import tempfile
from datetime import timedelta
import ipaddress
import threading
import pytest
from myapp.config import Config

def test_default_fallback():
    cfg = Config(defaults={'a': 1})
    data = cfg.load()
    assert data['a'] == 1

def test_toml_loader(tmp_path):
    toml_content = 'foo = "bar"\n[db]\nhost = "localhost"\n'
    f = tmp_path / "config.toml"
    f.write_bytes(toml_content.encode())
    cfg = Config(defaults={}, config_files=[str(f)])
    data = cfg.load()
    assert data['foo'] == "bar"
    assert data['db']['host'] == "localhost"

def test_env_loader(tmp_path, monkeypatch):
    monkeypatch.setenv('MYAPP_DB__HOST', '127.0.0.1')
    cfg = Config(defaults={})
    data = cfg.load()
    assert 'db' in data
    assert data['db']['host'] == '127.0.0.1'

def test_argv_loader(monkeypatch):
    defaults = {'db': {'host': 'initial'}, 'count': 5}
    monkeypatch.setenv('MYAPP_UNUSED', 'nope')
    testargs = ['prog', '--db-host', '192.168.0.1', '--count', '10']
    monkeypatch.setattr(sys, 'argv', testargs)
    cfg = Config(defaults=defaults)
    data = cfg.load()
    assert data['db']['host'] == '192.168.0.1'
    assert data['count'] == 10

def test_nested_merge_and_array_override(tmp_path):
    defaults = {'db': {'a': 1, 'b': 2}, 'mw': {'plugins': [1,2]}}
    toml_content = '[db]\nb = 3\nc = 4\n[mw]\nplugins = [3]\n'
    f = tmp_path / "config.toml"
    f.write_bytes(toml_content.encode())
    cfg = Config(defaults=defaults, config_files=[str(f)])
    data = cfg.load()
    assert data['db']['a'] == 1
    assert data['db']['b'] == 3
    assert data['db']['c'] == 4
    assert data['mw']['plugins'] == [3]

def test_custom_coercers_env(monkeypatch):
    def to_tdelta(s):
        return timedelta(seconds=int(s))
    monkeypatch.setenv('MYAPP_TIMEOUT', '60')
    cfg = Config(defaults={}, coercers={'timeout': to_tdelta})
    data = cfg.load()
    assert isinstance(data['timeout'], timedelta)
    assert data['timeout'].seconds == 60

def test_custom_coercers_ip(monkeypatch):
    def to_ip(s):
        return ipaddress.ip_address(s)
    monkeypatch.setenv('MYAPP_SERVER__ADDR', '192.0.2.1')
    cfg = Config(defaults={}, coercers={'server.addr': to_ip})
    data = cfg.load()
    assert isinstance(data['server']['addr'], ipaddress.IPv4Address)
    assert str(data['server']['addr']) == '192.0.2.1'

def test_watch_reload(tmp_path):
    # Prepare a config file and watcher
    toml_content1 = 'val = 1\n'
    toml_content2 = 'val = 2\n'
    f = tmp_path / "watch.toml"
    f.write_bytes(toml_content1.encode())
    cfg = Config(defaults={}, config_files=[str(f)])
    loaded = cfg.load()
    results = []
    def cb(data):
        results.append(data.get('val'))
    cfg.register_watch(cb)
    cfg.watch(interval=0.1)
    time.sleep(0.2)
    # Update file
    f.write_bytes(toml_content2.encode())
    time.sleep(0.3)
    assert 2 in results

def test_flatten_and_cli_generation(monkeypatch):
    defaults = {'section': {'opt': 1}, 'flag': False}
    testargs = ['prog', '--section-opt', '5', '--flag']
    monkeypatch.setattr(sys, 'argv', testargs)
    cfg = Config(defaults=defaults)
    data = cfg.load()
    assert data['section']['opt'] == 5
    assert data['flag'] is True
