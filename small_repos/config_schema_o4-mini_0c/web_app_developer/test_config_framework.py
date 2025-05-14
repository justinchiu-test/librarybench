import os
import time
import tempfile
import threading
import argparse
import pytest
from config_framework import Config, ConfigError

def test_load_yaml_and_merge(tmp_path):
    cfg_file = tmp_path / "config.yaml"
    cfg_file.write_text("a: 1\nb: two\n")
    cfg = Config(schema={'a': int, 'b': str})
    data = cfg.load_yaml(str(cfg_file))
    assert data == {'a': 1, 'b': 'two'}
    cfg.load_env_vars()  # empty
    merged = cfg.merge_configs()
    assert merged['a'] == 1 and merged['b'] == 'two'

def test_load_dotenv(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("# comment\nX=123\nY=hello\n")
    cfg = Config()
    data = cfg.load_dotenv(str(env_file))
    assert data == {'X': '123', 'Y': 'hello'}
    merged = cfg.merge_configs()
    assert merged['X'] == '123' and merged['Y'] == 'hello'

def test_load_env_vars(monkeypatch):
    monkeypatch.setenv('TESTKEY', 'VAL')
    cfg = Config()
    data = cfg.load_env_vars()
    assert 'TESTKEY' in data and data['TESTKEY'] == 'VAL'
    merged = cfg.merge_configs()
    assert merged['TESTKEY'] == 'VAL'

def test_override_cli_args():
    cfg = Config()
    args = ['--port=8080', '--host=localhost']
    out = cfg.override_cli_args(args)
    assert out == {'port': '8080', 'host': 'localhost'}
    merged = cfg.merge_configs()
    assert merged['port'] == '8080'

def test_runtime_override_and_programmatic_api():
    cfg = Config()
    cfg.set('x', 10)
    assert cfg.get('x') == 10
    cfg.set('x', 20)
    assert cfg.to_dict()['x'] == 20

def test_default_factory():
    cfg = Config()
    cfg.set_default_factory('rnd', lambda: 5)
    merged = cfg.merge_configs()
    assert merged['rnd'] == 5

def test_schema_type_validation():
    cfg = Config(schema={'num': int})
    cfg.set('num', 'not_int')
    with pytest.raises(ConfigError) as exc:
        cfg.get('num')
    assert "Expected" in str(exc.value)

def test_compose_schema():
    cfg = Config(schema={'a': int})
    cfg.compose_schema(sub1={'b': str}, sub2={'c': float})
    assert cfg._schema['a'] == int
    assert cfg._schema['b'] == str
    assert cfg._schema['c'] == float

def test_register_plugin_and_post(tmp_path):
    # loader plugin: add key 'loaded'
    def loader(data):
        data['loaded'] = True
    cfg = Config()
    cfg.register_plugin('loader', loader)
    merged = cfg.merge_configs()
    assert merged.get('loaded') is True

def test_register_validator_plugin():
    def validator(data, schema):
        if 'must' not in data:
            raise ConfigError("Missing 'must'")
    cfg = Config(schema={})
    cfg.register_plugin('validator', validator)
    with pytest.raises(ConfigError):
        cfg.merge_configs()

def test_watch_config_file(tmp_path):
    cfg_file = tmp_path / "w.yaml"
    cfg_file.write_text("val: 1\n")
    cfg = Config(schema={'val': int})
    cfg.load_yaml(str(cfg_file))
    cfg.watch_config_file(str(cfg_file), interval=0.1)
    time.sleep(0.2)
    # modify file
    cfg_file.write_text("val: 2\n")
    # wait for reload
    time.sleep(0.2)
    assert cfg.get('val') == 2

def test_load_yaml_no_pyyaml(monkeypatch, tmp_path):
    # simulate yaml is None
    import sys
    sys_modules = sys.modules
    orig_yaml = sys_modules.pop('yaml', None)
    try:
        import builtins
        setattr(builtins, '__import__', lambda name, *args, **kwargs: (_ for _ in ()).throw(ImportError()) if name=='yaml' else __import__(name, *args, **kwargs))
        from importlib import reload
        import config_framework
        reload(config_framework)
        cfg = config_framework.Config()
        with pytest.raises(ConfigError):
            cfg.load_yaml(str(tmp_path/"no.yaml"))
    finally:
        if orig_yaml:
            sys_modules['yaml'] = orig_yaml

def test_error_reporting():
    cfg = Config()
    with pytest.raises(ConfigError) as exc:
        cfg.report_error("oops", filename="f", lineno=10, section="s", key="k", expected=str, actual=int, suggestion="fix it")
    msg = str(exc.value)
    assert "File 'f'" in msg and "Line 10" in msg and "Section 's'" in msg and "Key 'k'" in msg and "Expected" in msg and "Suggestion" in msg
