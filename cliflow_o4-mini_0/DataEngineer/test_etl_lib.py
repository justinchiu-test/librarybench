import os
import sys
import tempfile
import configparser
import json
import io
import pytest

import etl_lib

def test_set_renderer():
    etl_lib.set_renderer('json')
    assert etl_lib.renderer == 'json'
    etl_lib.set_renderer('plain')
    assert etl_lib.renderer == 'plain'

def test_pipe():
    def add1(x):
        return x + 1
    def mul2(x):
        return x * 2
    fn = etl_lib.pipe(add1, mul2)
    assert fn(3) == 8

def test_parallelize():
    @etl_lib.parallelize
    def dummy():
        return None
    tasks = [lambda: 1, lambda: 2, lambda: 3]
    result = dummy(tasks=tasks)
    assert sorted(result) == [1, 2, 3]

def test_secure_input(monkeypatch):
    monkeypatch.setattr(etl_lib.getpass, 'getpass', lambda prompt: 'secret')
    manager = etl_lib.secure_input("Prompt: ")
    with manager as s:
        assert s == 'secret'
        assert manager.secret == 'secret'
    assert manager.secret is None

def test_translate():
    assert etl_lib.translate('hello', 'es') == 'hola'
    assert etl_lib.translate('bye', 'es') == 'adiós'
    assert etl_lib.translate('unknown', 'es') == 'unknown'

def test_export_workflow_markdown():
    def step1():
        "First step"
        pass
    def step2():
        "Second step"
        pass
    md = etl_lib.export_workflow([step1, step2], format='markdown')
    assert "# Workflow" in md
    assert "## step1" in md
    assert "First step" in md

def test_export_workflow_html():
    def step():
        "Doc"
        pass
    html = etl_lib.export_workflow([step], format='html')
    assert "<h1>Workflow</h1>" in html
    assert "<h2>step</h2>" in html
    assert "<p>Doc</p>" in html

def test_load_config_json(tmp_path):
    data = {'a': 1}
    p = tmp_path / "conf.json"
    p.write_text(json.dumps(data))
    assert etl_lib.load_config(str(p)) == data

def test_load_config_yaml(tmp_path):
    data = {'b': 2}
    p = tmp_path / "conf.yaml"
    p.write_text("b: 2")
    if etl_lib.yaml is None:
        with pytest.raises(ImportError):
            etl_lib.load_config(str(p))
    else:
        assert etl_lib.load_config(str(p)) == data

def test_load_config_toml(tmp_path):
    data = {'c': 3}
    p = tmp_path / "conf.toml"
    p.write_text("c = 3")
    if etl_lib.toml is None:
        with pytest.raises(ImportError):
            etl_lib.load_config(str(p))
    else:
        assert etl_lib.load_config(str(p)) == data

def test_load_config_ini(tmp_path):
    p = tmp_path / "conf.ini"
    content = "[section]\nx=1\ny=two"
    p.write_text(content)
    cfg = etl_lib.load_config(str(p))
    assert 'section' in cfg
    assert cfg['section']['x'] == '1'
    assert cfg['section']['y'] == 'two'

def test_env_inject(monkeypatch):
    monkeypatch.setenv('MYVAR', 'value')
    @etl_lib.env_inject
    def f(myvar):
        return myvar
    assert f() == 'value'

def test_load_plugins(tmp_path):
    plugin_dir = tmp_path / "plugins"
    plugin_dir.mkdir()
    plugin_file = plugin_dir / "plugin1.py"
    plugin_file.write_text("name = 'plugin1'")
    mods = etl_lib.load_plugins(str(plugin_dir))
    names = [getattr(m, 'name', None) for m in mods]
    assert 'plugin1' in names

def test_redirect_io():
    buf_out = io.StringIO()
    buf_err = io.StringIO()
    with etl_lib.redirect_io(stdout=buf_out, stderr=buf_err) as (out, err):
        print("hello")
        print("oops", file=sys.stderr)
    assert "hello" in buf_out.getvalue()
    assert "oops" in buf_err.getvalue()
