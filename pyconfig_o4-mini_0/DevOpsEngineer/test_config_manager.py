import os
import json
import threading
import pytest
from config_manager import ConfigManager

def test_merge_precedence():
    defaults = {'a': 1, 'b': {'x': 10}, 'c': 3}
    file_cfg = {'b': {'y': 20}, 'c': 4}
    cli = {'c': 5}
    merged = ConfigManager().merge_configs(defaults, file_cfg, cli)
    assert merged['a'] == 1
    assert merged['b']['x'] == 10
    assert merged['b']['y'] == 20
    assert merged['c'] == 5

def test_interpolate_env_and_config(tmp_path, monkeypatch):
    monkeypatch.setenv('TEST_ENV', 'home')
    defaults = {'path': '${ENV:TEST_ENV}/bin', 'home': '/usr'}
    cm = ConfigManager(defaults)
    cm.interpolate()
    assert cm.get('path') == 'home/bin'
    # test config var interpolation
    defaults2 = {'root': '${home}/root'}
    cm2 = ConfigManager(defaults2)
    cm2._config['home'] = '/usr'
    cm2.interpolate()
    assert cm2.get('root') == '/usr/root'

def test_getters_and_types():
    defaults = {'num': '123', 'flag1': 'True', 'flag2': 'false', 'text': 'hello'}
    cm = ConfigManager(defaults)
    assert cm.get_int('num') == 123
    assert cm.get_bool('flag1') is True
    assert cm.get_bool('flag2') is False
    assert cm.get_str('text') == 'hello'
    with pytest.raises(ValueError):
        cm.get_int('text')
    with pytest.raises(ValueError):
        cm.get_bool('text')

def test_section_access():
    defaults = {'database': {'primary': {'host': 'localhost'}}}
    cm = ConfigManager(defaults)
    section = cm.section('database.primary')
    assert isinstance(section, dict)
    assert section['host'] == 'localhost'
    with pytest.raises(ValueError):
        cm.section('database.primary.host')

def test_on_load_and_on_access_hooks():
    defaults = {'val': 1}
    cm = ConfigManager(defaults)
    loaded = []
    accessed = []
    cm.on_load('val', lambda v: loaded.append(v))
    cm.on_access('val', lambda v: accessed.append(v))
    # simulate load_file by calling load_file with same data
    import tempfile, json as _json
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.json')
    tmp.write(_json.dumps({'val': 2}).encode())
    tmp.close()
    cm.load_file(tmp.name)
    assert loaded == [2]
    # access
    v = cm.get('val')
    assert v == 2
    assert accessed == [2]

def test_diff_configs():
    a = {'a': 1, 'b': 2}
    b = {'a': 1, 'b': 3}
    diff = ConfigManager.diff(a, b)
    assert '-  "b": 2' in diff
    assert '+  "b": 3' in diff

def test_schema_validation_and_custom_validator():
    schema = {
        'port': {'type': int, 'required': True, 'min': 1, 'max': 65535},
        'host': {'type': str, 'required': True}
    }
    defaults = {'port': 8080, 'host': 'localhost'}
    cm = ConfigManager(defaults, schema=schema)
    # should pass
    cm.validate_schema()
    # invalid port
    cm2 = ConfigManager({'port': 70000, 'host': 'h'}, schema=schema)
    with pytest.raises(ValueError):
        cm2.validate_schema()
    # custom validator
    cm3 = ConfigManager({'port': 80, 'host': 'bad_host'}, schema=schema)
    def host_validator(v):
        if not v.startswith('good'):
            raise ValueError("host must start with 'good'")
    cm3.register_validator('host', host_validator)
    with pytest.raises(ValueError):
        cm3.validate_schema()
    # fix and pass
    cm3._config['host'] = 'good_host'
    cm3.validate_schema()

def test_generate_docs_markdown_and_html():
    schema = {
        'port': {'type': int, 'required': True, 'description': 'Port number', 'example': 8080},
        'debug': {'type': bool, 'required': False, 'description': 'Enable debug'}
    }
    cm = ConfigManager({}, schema=schema)
    md = cm.generate_docs(fmt='markdown')
    assert '## Configuration Documentation' in md
    assert '| port | int | yes | Port number | 8080 |' in md
    html = cm.generate_docs(fmt='html')
    assert '<h2>Configuration Documentation</h2>' in html
    assert '<h3>port</h3>' in html

def test_merge_with_env_vars(monkeypatch):
    monkeypatch.setenv('X', '1')
    defaults = {'x': '${X}', 'y': 2}
    cm = ConfigManager(defaults)
    cm.interpolate()
    assert cm.get_int('x') == 1

def test_thread_safety_decorator():
    cm = ConfigManager({'a': 1})
    # ensure methods are wrapped
    assert hasattr(cm.load_file, '__wrapped__')
    assert hasattr(cm.get, '__wrapped__')
    # test concurrent reads
    results = []
    def reader():
        for _ in range(10):
            results.append(cm.get('a'))
    threads = [threading.Thread(target=reader) for _ in range(5)]
    for t in threads: t.start()
    for t in threads: t.join()
    assert all(r == 1 for r in results)

def test_load_yaml(tmp_path, monkeypatch):
    if not hasattr(ConfigManager, 'load_file'):
        pytest.skip("YAML not supported")
    yaml_content = "k1: v1\nk2: ${ENV:TEST}\n"
    p = tmp_path / "test.yaml"
    p.write_text(yaml_content)
    monkeypatch.setenv('TEST', 'val')
    cm = ConfigManager()
    cfg = cm.load_file(str(p))
    assert cfg['k1'] == 'v1'
    assert cfg['k2'] == 'val'
