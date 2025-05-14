import os
import tempfile
import pytest
from config_system import Config

def test_dot_notation_set_get():
    cfg = Config()
    cfg.set('services.user.host', 'localhost')
    cfg.set('services.user.port', 8080)
    assert cfg.get('services.user.host') == 'localhost'
    assert cfg.get('services.user.port') == 8080

def test_nested_merge_and_conflict():
    cfg = Config()
    cfg.load_dict({'a': {'b': 1, 'c': {'d': [1,2]}}})
    cfg.load_dict({'a': {'c': {'d': [3,4], 'e': 5}}})
    assert cfg.get('a.b') == 1
    assert cfg.get('a.c.d') == [3,4]
    assert cfg.get('a.c.e') == 5
    with pytest.raises(ValueError):
        cfg.load_dict({'a': {'c': 'string'}})  # conflict with dict

def test_variable_interpolation_env_and_keys(monkeypatch):
    cfg = Config()
    monkeypatch.setenv('HOST', '127.0.0.1')
    cfg.set('host', '${HOST}')
    cfg.set('port', 9000)
    cfg.set('url', 'http://${host}:${port}/api')
    assert cfg.get('host') == '127.0.0.1'
    assert cfg.get('url') == 'http://127.0.0.1:9000/api'

def test_circular_interpolation():
    cfg = Config()
    cfg.set('a', '${b}')
    cfg.set('b', '${a}')
    with pytest.raises(ValueError):
        _ = cfg.get('a')

def test_watchers_triggered_on_set():
    cfg = Config()
    events = []
    def cb(key, old, new):
        events.append((key, old, new))
    cfg.register_watcher('x.y', cb)
    cfg.set('x.y', 1)
    cfg.set('x.y', 2)
    assert events == [('x.y', None, 1), ('x.y', 1, 2)]

def test_yaml_loader(tmp_path):
    cfg = Config()
    data = {'service': {'name': 'test', 'replicas': 3}}
    file = tmp_path / 'conf.yml'
    file.write_text("service:\n  name: test\n  replicas: 3\n")
    cfg.load_yaml(str(file))
    assert cfg.get('service.name') == 'test'
    assert cfg.get('service.replicas') == 3

def test_custom_coercer():
    cfg = Config()
    def to_int_range(val):
        lo, hi = map(int, val.split('-'))
        return (lo, hi)
    cfg.register_coercer('range', to_int_range)
    cfg.set('range', '10-20')
    assert cfg.get('range') == (10, 20)

def test_profiles_and_defaults():
    cfg = Config()
    cfg.add_default('db.host', 'default_host')
    cfg.load_dict({'db': {'host': 'base_host', 'port': 1234}})
    cfg.load_dict({'db': {'host': 'staging_host'}}, profile='staging')
    cfg.select_profile('staging')
    assert cfg.get('db.host') == 'staging_host'
    assert cfg.get('db.port') == 1234
    cfg.select_profile(None)
    assert cfg.get('db.host') == 'base_host'
    cfg2 = Config()
    cfg2.add_default('x.y', 'fallback')
    assert cfg2.get('x.y') == 'fallback'

def test_visualization():
    cfg = Config()
    cfg.add_default('a', 1)
    cfg.load_dict({'b': 2})
    cfg.load_dict({'c': 3}, profile='p')
    cfg.select_profile('p')
    vis = cfg.visualize()
    assert vis == {'a': 1, 'b': 2, 'c': 3}
