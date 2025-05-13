import os
import sys
import json
import configparser
import tempfile
import importlib
import pytest
import getpass

from security_audit import (
    set_renderer, render, register_renderer,
    pipe, parallelize, secure_input,
    translate, export_workflow, load_config,
    env_inject, load_plugins, redirect_io,
)

def test_renderers():
    set_renderer('plain')
    assert render("hello") == "hello"
    set_renderer('color')
    # color adds ANSI codes
    out = render("test")
    assert "\033[94mtest\033[0m" == out
    set_renderer('json')
    assert render({"a": 1}) == json.dumps({"a":1})
    set_renderer('markdown')
    md = render({"x": "y"})
    assert "- **x**: y" in md

def test_register_and_set_custom_renderer():
    def custom(data): return f"CUSTOM:{data}"
    register_renderer('custom', custom)
    set_renderer('custom')
    assert render("data") == "CUSTOM:data"

def test_pipe():
    def f1(x): return x + 1
    def f2(x): return x * 2
    chain = pipe(f1, f2)
    assert chain(3) == 8

def test_parallelize():
    def t1(): return 1
    def t2(): return 2
    results = parallelize(t1, t2)
    assert set(results) == {1, 2}

def test_secure_input(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda prompt: "inp")
    assert secure_input("?", password=False) == "inp"
    monkeypatch.setattr(getpass, 'getpass', lambda prompt: "pwd")
    assert secure_input("?", password=True) == "pwd"

def test_translate():
    assert translate("Hello", "es") == "[es] Hello"

def test_export_workflow():
    steps = ["scan", "report"]
    md = export_workflow(steps, fmt='md')
    assert md == "- scan\n- report"
    html = export_workflow(steps, fmt='html')
    assert html == "<ol><li>scan</li><li>report</li></ol>"
    with pytest.raises(ValueError):
        export_workflow(steps, fmt='txt')

def test_load_config_json(tmp_path):
    data = {"a":1}
    path = tmp_path / "c.json"
    path.write_text(json.dumps(data))
    cfg = load_config(str(path))
    assert cfg == data

def test_load_config_ini(tmp_path):
    path = tmp_path / "c.ini"
    content = "[sec]\nx=10\ny=foo"
    path.write_text(content)
    cfg = load_config(str(path))
    assert cfg == {"sec": {"x":"10", "y":"foo"}}

def test_load_config_unsupported(tmp_path):
    path = tmp_path / "c.txt"
    path.write_text("data")
    with pytest.raises(ValueError):
        load_config(str(path))

def test_env_inject(monkeypatch):
    monkeypatch.setenv('SCAN_TARGET', 'localhost')
    monkeypatch.setenv('API_TOKEN', 'abcd')
    flags = env_inject()
    assert '--scan-target' in flags and 'localhost' in flags
    assert '--api-token' in flags and 'abcd' in flags

def test_load_plugins(tmp_path):
    # create a dummy plugin file
    p = tmp_path / "plug.py"
    p.write_text("value = 123")
    modules = load_plugins([str(p)])
    assert len(modules) == 1
    mod = modules[0]
    assert hasattr(mod, 'value') and mod.value == 123

def test_redirect_io(tmp_path):
    out_path = tmp_path / "out.txt"
    err_path = tmp_path / "err.txt"
    with redirect_io(str(out_path), str(err_path)):
        print("hello")
        print("oops", file=sys.stderr)
    assert out_path.read_text().strip() == "hello"
    assert err_path.read_text().strip() == "oops"
