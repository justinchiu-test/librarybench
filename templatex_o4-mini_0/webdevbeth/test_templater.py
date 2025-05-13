import pytest
import shlex
import json
import time
from templater import (
    escape, minify, build_graph, render_expr,
    if_block, stream_render, assert_render,
    profile_render, enable_sandbox, precompile
)

def test_escape_html():
    assert escape('html', '<div>') == '&lt;div&gt;'
    assert escape('html', 'Tom & Jerry') == 'Tom &amp; Jerry'

def test_escape_json():
    text = 'He said "Hello"'
    assert escape('json', text) == json.dumps(text)

def test_escape_shell():
    text = "some text"
    assert escape('shell', text) == shlex.quote(text)
    text2 = "a'b"
    assert escape('shell', text2) == shlex.quote(text2)

def test_escape_invalid_mode():
    with pytest.raises(ValueError):
        escape('xml', 'test')

def test_minify():
    tpl = "<html>  <!-- comment -->\n<body>   Hello </body>\n</html>"
    result = minify(tpl)
    assert result == "<html> <body> Hello </body> </html>"

def test_build_graph():
    assert isinstance(build_graph(), dict)
    assert build_graph() == {}

def test_render_expr_literals():
    assert render_expr("1 + 2") == 3
    assert render_expr("5 > 3") is True
    assert render_expr("False or True") is True
    assert render_expr("-5") == -5

def test_render_expr_invalid():
    with pytest.raises(ValueError):
        render_expr("import os")

def test_if_block():
    # simple if
    assert if_block(True, "yes", [], "no") == "yes"
    assert if_block(False, "yes", [], "no") == "no"
    # with elifs
    elifs = [(False, "e1"), (True, "e2")]
    assert if_block(False, "yes", elifs, "no") == "e2"
    # no match in elifs
    elifs2 = [(False, "e1"), (False, "e2")]
    assert if_block(False, "yes", elifs2, "no") == "no"

def test_stream_render():
    tpl = "Hello {{name}}!"
    gen = stream_render(tpl, {'name': 'Alice'})
    chunks = list(gen)
    assert chunks == ["Hello Alice!"]

def test_assert_render_success():
    tpl = "Sum: {{a + b}}"
    assert_render(tpl, {'a': 2, 'b': 3}, "Sum: 5")

def test_assert_render_failure():
    tpl = "Sum: {{a + b}}"
    with pytest.raises(AssertionError):
        assert_render(tpl, {'a': 2, 'b': 2}, "Sum: 5")

def test_profile_render():
    tpl = "X"
    ctx = {}
    prof = profile_render(tpl, ctx)
    assert set(prof.keys()) == {'parsing', 'compilation', 'rendering'}
    for v in prof.values():
        assert isinstance(v, float)
        assert v >= 0

def test_enable_sandbox():
    # no direct effect, but should not error
    enable_sandbox()

def test_precompile_cache():
    tpl = "template"
    c1 = precompile(tpl)
    c2 = precompile(tpl)
    assert c1 is c2
