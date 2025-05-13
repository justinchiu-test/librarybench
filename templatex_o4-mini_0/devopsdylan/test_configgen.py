import os
import pytest
import time
import shutil
from configgen import (
    escape, minify, build_graph, render_expr, if_block,
    render, stream_render, assert_render, profile_render,
    enable_sandbox, precompile, SANDBOX_ENABLED
)

def test_escape_shell():
    text = "hello world"
    escaped = escape('shell', text)
    assert escaped.startswith("'") and escaped.endswith("'")

def test_escape_json():
    text = 'He said "hi"'
    assert escape('json', text) == '"He said \\"hi\\""'

def test_escape_html():
    text = '<div>test</div>'
    assert escape('html', text) == '&lt;div&gt;test&lt;/div&gt;'

def test_escape_invalid():
    with pytest.raises(ValueError):
        escape('invalid', 'text')

def test_minify():
    tpl = """
    # This is a comment
    line1

      # another comment
    line2   line3
    """
    assert minify(tpl) == "line1 line2   line3"

def test_build_graph(tmp_path, monkeypatch):
    d = tmp_path / "templates"
    d.mkdir()
    a = d / "a.tpl"
    b = d / "b.tpl"
    a.write_text("start\n{% include 'b.tpl' %}\nend")
    b.write_text("content")
    monkeypatch.chdir(tmp_path / "templates")
    graph = build_graph()
    assert 'a.tpl' in graph
    assert graph['a.tpl'] == ['b.tpl']

def test_render_expr_arithmetic():
    assert render_expr('1+2*3') == 7

def test_render_expr_comparison():
    assert render_expr('5 > 3') is True

def test_render_expr_boolean():
    assert render_expr('True and False') is False

def test_render_expr_division():
    assert abs(render_expr('5/2') - 2.5) < 1e-6

def test_render_expr_unsafe_name():
    with pytest.raises(ValueError):
        render_expr('__import__("os").system("ls")')

def test_if_block_true():
    result = if_block('1==1', 'yes', [('0', 'no')], 'else')
    assert result == 'yes'

def test_if_block_elif():
    result = if_block('0', 'yes', [('1', 'no')], 'else')
    assert result == 'no'

def test_if_block_else():
    result = if_block('0', 'yes', [('0', 'no')], 'else')
    assert result == 'else'

def test_render_and_stream():
    tpl = "Line1 {val}\nLine2"
    ctx = {'val': 'X'}
    full = render(tpl, ctx)
    assert full == "Line1 X\nLine2"
    parts = list(stream_render(tpl, ctx))
    assert parts == ["Line1 X\n", "Line2"]

def test_assert_render_success():
    assert_render("Hello {name}", {'name': 'Bob'}, "Hello Bob")

def test_assert_render_failure():
    with pytest.raises(AssertionError):
        assert_render("Hi {name}", {'name': 'Bob'}, "Hello Bob")

def test_profile_render():
    tpl = "Test {x}"
    ctx = {'x': 'Y'}
    times = profile_render(tpl, ctx)
    assert set(times.keys()) == {'parsing', 'compilation', 'rendering'}
    assert all(isinstance(v, float) for v in times.values())

def test_enable_sandbox():
    # SANDBOX_ENABLED is initially False
    assert SANDBOX_ENABLED is False
    enable_sandbox()
    from configgen import SANDBOX_ENABLED as flag
    assert flag is True

def test_precompile():
    tpl = "Foo {bar}"
    fn = precompile(tpl)
    assert callable(fn)
    assert fn({'bar': 'Baz'}) == "Foo Baz"
