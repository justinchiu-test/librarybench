import os
import json
import configparser
import pytest
from config_manager import ConfigManager

def test_inherit_schema():
    base = {'a': 1, 'b': {'c': 2}}
    override = {'b': {'d': 3}, 'e': 4}
    cm = ConfigManager()
    result = cm.inherit_schema(base, override)
    assert result['a'] == 1
    assert result['b']['c'] == 2
    assert result['b']['d'] == 3
    assert result['e'] == 4

def test_lazy_load_section():
    cm = ConfigManager()
    loader_called = {'count': 0}
    def loader():
        loader_called['count'] += 1
        return {'x': 10}
    cm.lazy_load_section('large', loader)
    assert 'large' not in cm.config
    section = cm.get('large')
    assert section == {'x': 10}
    assert loader_called['count'] == 1
    # second get doesn’t call loader again
    section2 = cm.get('large')
    assert loader_called['count'] == 1
    assert section2 == section

def test_set_validation_context_and_validate_lab():
    cm = ConfigManager()
    cm.config = {'memory_limit': 400}
    cm.set_validation_context('lab')
    with pytest.raises(ValueError):
        cm.validate()
    cm.config['memory_limit'] = 600
    cm.validate()  # no error

def test_set_validation_context_and_validate_field():
    cm = ConfigManager()
    cm.config = {'network': {}}
    cm.set_validation_context('field')
    with pytest.raises(ValueError):
        cm.validate()
    cm.config['network'] = {'ssid': 's', 'password': 'p'}
    cm.validate()

def test_load_config_json(tmp_path):
    data = {'key': 'value'}
    f = tmp_path / "cfg.json"
    f.write_text(json.dumps(data))
    cm = ConfigManager()
    result = cm.load_config(str(f))
    assert result['key'] == 'value'
    assert cm.config['key'] == 'value'

def test_load_config_ini(tmp_path):
    parser = configparser.ConfigParser()
    parser['section'] = {'k': 'v'}
    f = tmp_path / "cfg.ini"
    with open(f, 'w') as fp:
        parser.write(fp)
    cm = ConfigManager()
    result = cm.load_config(str(f))
    assert 'section' in result
    assert result['section']['k'] == 'v'

def test_load_env_file(tmp_path, monkeypatch):
    env_content = "FOO=bar\n# comment\nBAZ=qux\n"
    f = tmp_path / ".env"
    f.write_text(env_content)
    cm = ConfigManager()
    envs = cm.load_env_file(str(f))
    assert envs['FOO'] == 'bar'
    assert envs['BAZ'] == 'qux'
    assert os.environ['FOO'] == 'bar'
    assert cm.env_vars['BAZ'] == 'qux'

def test_register_and_run_plugins():
    cm = ConfigManager()
    def plugin1(data):
        data['x'] = 1
        return data
    def plugin2(data):
        data['y'] = data.get('x', 0) + 2
        return data
    cm.register_plugin(plugin1)
    cm.register_plugin(plugin2)
    data = {}
    result = cm.run_plugins(data)
    assert result['x'] == 1
    assert result['y'] == 3

def test_apply_defaults():
    cm = ConfigManager()
    cm.config = {'timeout': 10}
    cm.apply_defaults()
    # existing override preserved
    assert cm.config['timeout'] == 10
    # defaults filled
    assert cm.config['sampling_interval'] == 60
    assert cm.config['memory_limit'] == 1024

def test_compose_schemas():
    schemas = [{'a': 1}, {'b': 2}, {'a': 3}]
    cm = ConfigManager()
    result = cm.compose_schemas(schemas)
    assert result['a'] == 3
    assert result['b'] == 2
    # config updated
    assert cm.config['a'] == 3

def test_expand_env_vars(monkeypatch):
    monkeypatch.setenv('FOO', 'bar')
    cm = ConfigManager()
    cm.config = {
        'x': 'pre_$FOO_post',
        'y': ['${FOO}', 'no'],
        'z': {'inner': '$FOO'}
    }
    cm.expand_env_vars()
    assert cm.config['x'] == 'pre_bar_post'
    assert cm.config['y'] == ['bar', 'no']
    assert cm.config['z']['inner'] == 'bar'

def test_prompt_for_missing(monkeypatch):
    cm = ConfigManager()
    cm.config = {}
    inputs = iter(['myssid', 'mypassword'])
    monkeypatch.setattr('builtins.input', lambda prompt: next(inputs))
    cm.prompt_for_missing()
    assert cm.config['network']['ssid'] == 'myssid'
    assert cm.config['network']['password'] == 'mypassword'
