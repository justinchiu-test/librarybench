import os
import sys
import json
import configparser
import tempfile
import getpass
import pytest
from cli import (
    set_renderer, get_renderer, pipe, parallelize,
    secure_input, translate, export_workflow,
    load_config, env_inject, load_plugins,
    redirect_io
)

def test_set_renderer_valid():
    set_renderer('color')
    assert get_renderer() == 'color'
    set_renderer('plain')
    assert get_renderer() == 'plain'
    set_renderer('json')
    assert get_renderer() == 'json'
    set_renderer('markdown')
    assert get_renderer() == 'markdown'

def test_set_renderer_invalid():
    with pytest.raises(ValueError):
        set_renderer('invalid')

def test_pipe_chain():
    def f(x): return x + 1
    def g(x): return x * 2
    p = pipe(f, g)
    assert p(3) == 8

def test_parallelize():
    def a(): return 'A'
    def b(): return 'B'
    results = parallelize([a, b])
    assert set(results) == {'A', 'B'}

def test_secure_input(monkeypatch):
    monkeypatch.setattr(getpass, 'getpass', lambda prompt='': 'secret123')
    sec = secure_input('Enter:')
    assert sec == 'secret123'

def test_translate():
    assert translate('hello', 'es') == 'hola'
    assert translate('help', 'fr') == 'aide'
    # fallback to key
    assert translate('unknown', 'es') == 'unknown'
    assert translate('hello', 'de') == 'hello'

def test_export_workflow_markdown():
    steps = [{'name': 'build', 'description': 'Compile code'},
             {'name': 'deploy', 'description': 'Deploy service'}]
    md = export_workflow(steps, format='markdown')
    assert "- build: Compile code" in md
    assert "- deploy: Deploy service" in md

def test_export_workflow_html():
    steps = [{'name': 'build', 'description': 'Compile code'}]
    html = export_workflow(steps, format='html')
    assert "<ul>" in html and "</ul>" in html
    assert "<li>build: Compile code</li>" in html

def test_export_workflow_invalid():
    with pytest.raises(ValueError):
        export_workflow([], format='txt')

def test_load_config_json(tmp_path):
    data = {'a': 1, 'b': 'two'}
    p = tmp_path / "conf.json"
    p.write_text(json.dumps(data))
    loaded = load_config(str(p))
    assert loaded == data

def test_load_config_ini(tmp_path):
    cfg = configparser.ConfigParser()
    cfg['sect'] = {'k': 'v'}
    p = tmp_path / "conf.ini"
    with open(p, 'w') as f:
        cfg.write(f)
    loaded = load_config(str(p))
    assert loaded == {'sect': {'k': 'v'}}

@pytest.mark.skipif(yaml is None, reason="PyYAML not installed")
def test_load_config_yaml(tmp_path):
    import yaml
    data = {'x': 10}
    p = tmp_path / "conf.yaml"
    p.write_text(yaml.dump(data))
    loaded = load_config(str(p))
    assert loaded == data

@pytest.mark.skipif(toml is None, reason="toml not installed")
def test_load_config_toml(tmp_path):
    import toml
    data = {'x': 5}
    p = tmp_path / "conf.toml"
    p.write_text(toml.dumps(data))
    loaded = load_config(str(p))
    assert loaded == data

def test_load_config_invalid(tmp_path):
    p = tmp_path / "conf.txt"
    p.write_text("data")
    with pytest.raises(ValueError):
        load_config(str(p))

def test_env_inject_dict(monkeypatch):
    monkeypatch.setenv('TEST_VAR', 'value1')
    args = {}
    mapping = {'TEST_VAR': 'test'}
    out = env_inject(args, mapping)
    assert out['test'] == 'value1'

class Dummy:
    pass

def test_env_inject_namespace(monkeypatch):
    monkeypatch.setenv('UVAR', 'uval')
    ns = Dummy()
    mapping = {'UVAR': 'var'}
    out = env_inject(ns, mapping)
    assert hasattr(out, 'var')
    assert out.var == 'uval'

def test_load_plugins(tmp_path):
    plugin_dir = tmp_path / "plugins"
    plugin_dir.mkdir()
    p = plugin_dir / "plug.py"
    p.write_text("plugin_var = 123")
    plugins = load_plugins(str(plugin_dir))
    assert 'plug' in plugins
    mod = plugins['plug']
    assert hasattr(mod, 'plugin_var') and mod.plugin_var == 123

def test_redirect_io(tmp_path):
    fpath = tmp_path / "log.txt"
    # ensure file exists
    fpath.write_text("")
    with redirect_io(str(fpath)):
        print("out")
        print("err", file=sys.stderr)
    content = fpath.read_text()
    assert "out" in content
    assert "err" in content
