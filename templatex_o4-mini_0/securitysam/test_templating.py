import os
import tempfile
import ast
import pytest
import time
import shutil
import json
import shlex

from templating import (
    escape, minify, build_graph, render_expr, if_block,
    stream_render, assert_render, profile_render,
    enable_sandbox, precompile
)

def test_escape_html():
    raw = '5 > 3 & 2 < 4 "quote" \'apos\''
    escaped = escape('html', raw)
    assert '&gt;' in escaped
    assert '&amp;' in escaped
    assert '&lt;' in escaped
    assert '&quot;' in escaped
    assert '&#x27;' in escaped

def test_escape_json():
    raw = 'Text\nwith "quotes" and \\slashes\\'
    j = escape('json', raw)
    # Should be valid JSON string literal
    parsed = json.loads(j)
    assert parsed == raw

def test_escape_shell():
    raw = 'some $(rm -rf /) text'
    s = escape('shell', raw)
    assert s == shlex.quote(raw)

def test_minify():
    tpl = """
    <html>
    <!-- comment -->
    <body>  Text    here </body>
    </html>
    """
    m = minify(tpl)
    assert '<!--' not in m
    assert '  ' not in m
    assert m.startswith('<html>')
    assert m.endswith('</html>')

def test_build_graph(tmp_path):
    # Create a fake template directory
    d = tmp_path / "templates"
    d.mkdir()
    a = d / "a.tpl"
    b = d / "b.tpl"
    c = d / "c.tpl"
    a.write_text("{% include 'b.tpl' %} hello")
    b.write_text("{% include \"c.tpl\" %} world")
    c.write_text("leaf")
    graph = build_graph(str(d))
    assert graph.get('a.tpl') == ['b.tpl']
    assert graph.get('b.tpl') == ['c.tpl']
    assert graph.get('c.tpl') == []

def test_render_expr_safe():
    assert render_expr("1 + 2 * (3 - 4) / 5") == 1 + 2 * (3 - 4) / 5
    assert render_expr("True and False or True") is True
    with pytest.raises(ValueError):
        render_expr("__import__('os').system('ls')")

def test_render_expr_sandbox():
    enable_sandbox()
    # In sandbox, variables are disallowed
    with pytest.raises(ValueError):
        render_expr("1 + x")

def test_if_block():
    block = if_block("x>0", "yes", elifs=[("x==0","zero")], else_="no")
    expected = "{% if x>0 %}yes{% elif x==0 %}zero{% else %}no{% endif %}"
    assert block == expected

def test_stream_render():
    tpl = "Hello {name}!"
    chunks = list(stream_render(tpl, {"name":"World"}, chunk_size=5))
    assert "".join(chunks) == "Hello World!"
    # Each chunk at most 5 chars
    assert all(len(c) <= 5 for c in chunks)

def test_assert_render_pass():
    assert_render("Hi {a}", {"a":"there"}, "Hi there")

def test_assert_render_fail():
    with pytest.raises(AssertionError):
        assert_render("Hi {a}", {"a":"you"}, "Hi there")

def test_profile_render():
    tpl = "1+2"
    times = profile_render(tpl, {})
    assert set(times.keys()) == {"parse", "compile", "render"}
    # Times should be floats >=0
    for v in times.values():
        assert isinstance(v, float)
        assert v >= 0

def test_precompile_caching():
    t = "1+1"
    tree1 = precompile(t)
    tree2 = precompile(t)
    assert isinstance(tree1, ast.AST)
    assert tree1 is tree2

def test_build_graph_empty(tmp_path):
    # Empty directory -> empty graph
    d = tmp_path / "empty"
    d.mkdir()
    g = build_graph(str(d))
    assert g == {}
