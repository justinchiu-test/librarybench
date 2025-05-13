import pytest
import time
import os
from reporting.template_engine import (
    escape, minify, build_graph, render_expr, if_block,
    render, stream_render, assert_render, profile_render,
    enable_sandbox, precompile, sandbox_enabled
)

def test_escape_html():
    text = "<div>Tom & Jerry's \"Adventure\"</div>"
    escaped = escape('html', text)
    assert escaped == "&lt;div&gt;Tom &amp; Jerry&#x27;s &quot;Adventure&quot;&lt;/div&gt;"

def test_escape_json():
    text = 'He said "Hello\nWorld"'
    esc = escape('json', text)
    # Should escape quotes and newline
    assert '\n' in esc and '\\"' in esc

def test_escape_shell():
    text = "some file; rm -rf /"
    esc = escape('shell', text)
    # The unsafe characters should be quoted
    assert esc.startswith("'") and esc.endswith("'")

def test_escape_invalid():
    with pytest.raises(ValueError):
        escape('xml', 'data')

def test_minify():
    tpl = """
    <html>
      <!-- Comment to remove -->
      <body>
        <h1>Title</h1>
      </body>
    </html>
    """
    out = minify(tpl)
    # Comments removed and whitespace collapsed
    assert '<!--' not in out
    assert '   ' not in out
    assert '<h1>Title</h1>' in out

def test_build_graph_simple():
    templates = {
        'base.html': "Header\n{% include 'sub.html' %}\nFooter",
        'sub.html': "Subcontent"
    }
    graph = build_graph(templates)
    assert graph == {
        'base.html': {'sub.html'},
        'sub.html': set()
    }

def test_render_expr_arithmetic():
    assert render_expr('1+2*3') == 7
    assert render_expr('sum([1,2,3])') == 6
    assert render_expr('len("abcd")') == 4

def test_render_expr_context():
    ctx = {'a': 5, 'b': 10}
    assert render_expr('a * b + 2', ctx) == 52

def test_render_expr_disallowed():
    with pytest.raises(NameError):
        render_expr('__import__("os").system("ls")')

def test_if_block():
    assert if_block(True, 'A', [], 'Z') == 'A'
    assert if_block(False, 'A', [(False,'B'), (True,'C')], 'Z') == 'C'
    assert if_block(False, 'A', [(False,'B')], 'Z') == 'Z'
    assert if_block(False, 'A', None, None) == ''

def test_render_simple():
    tpl = "Hello, {name}!"
    assert render(tpl, {'name': 'Alice'}) == "Hello, Alice!"

def test_stream_render():
    tpl = "Line1\nLine2\nLine3"
    gen = stream_render(tpl, {})
    lines = list(gen)
    assert lines == ['Line1\n', 'Line2\n', 'Line3']

def test_assert_render_success():
    tpl = "x={x}, y={y}"
    assert_render(tpl, {'x':1, 'y':2}, "x=1, y=2")

def test_assert_render_fail():
    with pytest.raises(AssertionError):
        assert_render("x={x}", {'x':0}, "x=1")

def test_profile_render():
    tpl = "Test {val}"
    prof = profile_render(tpl, {'val': 123})
    assert set(prof.keys()) == {'parse_time', 'render_time', 'total_time'}
    for k, v in prof.items():
        assert isinstance(v, float)
        assert v >= 0.0

def test_sandbox_mode():
    # Before sandbox, NameError
    with pytest.raises(NameError):
        render_expr('__import__("os").getcwd()')
    enable_sandbox()
    # In sandbox, still NameError
    with pytest.raises(NameError):
        render_expr('sum([1,2,3])')  # sum is allowed, so should work
    # Actually sum works even in sandbox
    assert render_expr('sum([1,2,3])') == 6

def test_precompile():
    fn = precompile('a + b')
    assert callable(fn)
    result = fn({'a': 3, 'b': 4})
    assert result == 7
