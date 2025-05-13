import os
import json
import configparser
import pytest
from configtool import ConfigManager

def test_load_config_json(tmp_path):
    file = tmp_path / "config.json"
    data = {"a": 1, "b": "two"}
    file.write_text(json.dumps(data))
    mgr = ConfigManager()
    cfg = mgr.load_config(str(file))
    assert cfg == data

def test_load_config_ini(tmp_path):
    file = tmp_path / "config.ini"
    content = "[section1]\na = 1\nb = two\n"
    file.write_text(content)
    mgr = ConfigManager()
    cfg = mgr.load_config(str(file))
    assert "section1" in cfg
    assert cfg["section1"]["a"] == "1"
    assert cfg["section1"]["b"] == "two"

def test_load_config_unsupported(tmp_path):
    file = tmp_path / "config.txt"
    file.write_text("key=value")
    mgr = ConfigManager()
    with pytest.raises(ValueError):
        mgr.load_config(str(file))

def test_load_env_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    env_file = tmp_path / ".env"
    env_file.write_text("""
# comment
KEY1=value1
KEY2="value2"
INVALIDLINE
KEY3='value3'
""")
    mgr = ConfigManager()
    env = mgr.load_env_file()
    assert env == {"KEY1": "value1", "KEY2": "value2", "KEY3": "value3"}

def test_expand_env_vars(monkeypatch):
    monkeypatch.setenv("TESTVAR", "hello")
    mgr = ConfigManager()
    cfg = {"path": "$TESTVAR/world", "nested": {"p": "$TESTVAR"}}
    expanded = mgr.expand_env_vars(cfg)
    assert expanded["path"] == "hello/world"
    assert expanded["nested"]["p"] == "hello"

def test_apply_defaults_and_compose():
    mgr = ConfigManager()
    mgr.global_schema['defaults'] = {'a': 1}
    mgr.project_schema['defaults'] = {'b': 2}
    mgr.user_schema['defaults'] = {'c': 3}
    mgr.register_plugin('p1', schema={'required': [], 'defaults': {'d': 4}})
    cfg = {}
    mgr.apply_defaults(cfg)
    assert cfg == {'a': 1, 'b': 2, 'c': 3, 'd': 4}
    composed = mgr.compose_schemas()
    assert set(composed['defaults'].items()) == set({'a': 1, 'b': 2, 'c': 3, 'd': 4}.items())

def test_inherit_schema():
    mgr = ConfigManager()
    base = {'x': 1, 'nested': {'a': 1, 'b': 2}}
    override = {'nested': {'b': 3, 'c': 4}, 'y': 2}
    result = mgr.inherit_schema(base, override)
    assert result == {'x': 1, 'nested': {'a': 1, 'b': 3, 'c': 4}, 'y': 2}

def test_prompt_for_missing(monkeypatch):
    mgr = ConfigManager()
    mgr.global_schema['required'] = ['a', 'b']
    inp = iter(["val_a", "val_b"])
    monkeypatch.setattr('builtins.input', lambda prompt: next(inp))
    cfg = {}
    mgr.prompt_for_missing(cfg)
    assert cfg['a'] == 'val_a'
    assert cfg['b'] == 'val_b'

def test_set_validation_context_and_validate():
    mgr = ConfigManager()
    mgr.global_schema['required'] = ['a']
    cfg = {}
    mgr.set_validation_context('interactive')
    mgr.validate(cfg)  # no error
    mgr.set_validation_context('ci')
    with pytest.raises(ValueError):
        mgr.validate(cfg)
    with pytest.raises(ValueError):
        mgr.set_validation_context('invalid')

def test_compose_schemas_order():
    mgr = ConfigManager()
    mgr.global_schema['required'] = ['a']
    mgr.global_schema['defaults'] = {'a': 1}
    mgr.project_schema['required'] = ['b']
    mgr.project_schema['defaults'] = {'b': 2}
    mgr.user_schema['required'] = ['c']
    mgr.user_schema['defaults'] = {'c': 3}
    mgr.register_plugin('p1', schema={'required': ['d'], 'defaults': {'d': 4}})
    composed = mgr.compose_schemas()
    assert composed['required'] == ['a', 'b', 'c', 'd']
    assert composed['defaults'] == {'a': 1, 'b': 2, 'c': 3, 'd': 4}

def test_register_and_lazy_load_plugin():
    mgr = ConfigManager()
    def loader(raw):
        raw['added'] = 'yes'
        return raw
    mgr.register_plugin('plug', loader=loader)
    cfg = {'plug': {'k1': 'v1'}}
    mgr.lazy_load_section(cfg, 'plug')
    assert cfg['plug']['k1'] == 'v1'
    assert cfg['plug']['added'] == 'yes'
    # second load should not add again
    mgr.lazy_load_section(cfg, 'plug')
    # still only one 'added'
    assert cfg['plug']['added'] == 'yes'

def test_plugin_validator(monkeypatch):
    mgr = ConfigManager()
    def validator(conf):
        if conf.get('fail'):
            raise ValueError("Plugin failure")
    mgr.register_plugin('plug', validator=validator)
    cfg = {'plug': {'fail': True}}
    mgr.set_validation_context('interactive')
    with pytest.raises(ValueError):
        mgr.validate(cfg)
