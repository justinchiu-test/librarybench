import os
import io
import tempfile
import getpass
import pytest
import configparser
import json

# Ensure yaml and tomllib names exist for the skipif decorators
try:
    import yaml
except ImportError:
    yaml = None

try:
    import tomllib
except ImportError:
    tomllib = None

from localization import (
    set_renderer, current_renderer, pipe, parallelize, secure_input,
    translate, export_workflow, load_config, env_inject, load_plugins,
    redirect_io
)

def test_set_renderer_valid():
    assert set_renderer('table') == 'table'
    assert current_renderer == 'table'
    assert set_renderer('json') == 'json'
    assert current_renderer == 'json'

def test_set_renderer_invalid():
    with pytest.raises(ValueError):
        set_renderer('xml')

def test_pipe_single_checker():
    resources = ['a', 'b']
    def up(x): return x.upper()
    result = pipe(resources, up)
    assert result == ['A', 'B']

def test_pipe_multiple_checkers():
    resources = ['x']
    def add_ex(x): return x + '!'
    def rev(x): return x[::-1]
    result = pipe(resources, add_ex, rev)
    assert result == ['!x']

def test_parallelize():
    def f1(): return 1
    def f2(): return 2
    def f3(): return 3
    results = parallelize(f1, f2, f3)
    assert set(results) == {1, 2, 3}

def test_secure_input(monkeypatch):
    monkeypatch.setattr(getpass, 'getpass', lambda prompt: 'SECRET')
    val = secure_input('Enter:')
    assert val == 'SECRET'

def test_translate_existing():
    trans = {'fr': {'Hello': 'Bonjour'}}
    assert translate('Hello', trans, 'fr') == 'Bonjour'

def test_translate_missing_locale():
    trans = {'es': {'Hi': 'Hola'}}
    assert translate('Hi', trans, 'fr') == 'Hi'

def test_export_workflow_markdown():
    md = export_workflow('markdown')
    assert md.startswith('# Workflow Guide')

def test_export_workflow_html():
    html = export_workflow('html')
    assert '<h1>' in html

def test_export_workflow_invalid():
    with pytest.raises(ValueError):
        export_workflow('pdf')

def test_load_config_json(tmp_path):
    data = {'a': 1, 'b': 2}
    p = tmp_path / 'test.json'
    p.write_text(json.dumps(data))
    cfg = load_config(str(p))
    assert cfg == data

def test_load_config_ini(tmp_path):
    cfg = configparser.ConfigParser()
    cfg['sec'] = {'k': 'v'}
    p = tmp_path / 'test.ini'
    with open(p, 'w') as f:
        cfg.write(f)
    loaded = load_config(str(p))
    assert loaded == {'sec': {'k': 'v'}}

@pytest.mark.skipif(yaml is None, reason="yaml not installed")
def test_load_config_yaml(tmp_path):
    import yaml
    data = {'x': 10}
    p = tmp_path / 'test.yaml'
    p.write_text(yaml.dump(data))
    loaded = load_config(str(p))
    assert loaded == data

@pytest.mark.skipif(tomllib is None, reason="tomllib not available")
def test_load_config_toml(tmp_path):
    data = {'one': 1}
    p = tmp_path / 'test.toml'
    p.write_text('one = 1\n')
    loaded = load_config(str(p))
    assert loaded == data

def test_env_inject(monkeypatch):
    monkeypatch.setenv('FOO', 'BAR')
    @env_inject
    def f(foo=None):
        return foo
    assert f() == 'BAR'
    # override in call
    assert f(foo='baz') == 'baz'

def test_load_plugins(tmp_path):
    plugins_dir = tmp_path / 'plugins'
    plugins_dir.mkdir()
    p = plugins_dir / 'plugin_test.py'
    p.write_text('VALUE = 42\n')
    mods = load_plugins(str(plugins_dir))
    assert len(mods) == 1
    mod = mods[0]
    assert hasattr(mod, 'VALUE') and mod.VALUE == 42

def test_redirect_io_stringio():
    buf = io.StringIO()
    with redirect_io('any', buf):
        print('hello')
    assert buf.getvalue().strip() == 'hello'

def test_redirect_io_file(tmp_path):
    p = tmp_path / 'out.txt'
    with redirect_io('file', str(p)):
        print('world')
    content = p.read_text().strip()
    assert content == 'world'
