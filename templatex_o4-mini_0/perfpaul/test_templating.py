import pytest
import os
from templating import (
    escape, minify, build_graph, render_expr,
    if_block, stream_render, assert_render,
    profile_render, enable_sandbox, precompile, _cache
)

def test_escape_html():
    assert escape('html', '<&">') == '&lt;&amp;&quot;&gt;'

def test_escape_json():
    assert escape('json', 'he\n"llo') == 'he\\n\\"llo'

def test_escape_shell():
    text = "abc def"
    out = escape('shell', text)
    # Should escape the space
    assert ' ' not in out

def test_escape_invalid():
    with pytest.raises(ValueError):
        escape('xml', 'text')

def test_minify():
    tpl = "  <div> <!-- comment --> Hello   World </div> "
    assert minify(tpl) == '<div> Hello World </div>'

def test_build_graph_single():
    tpl = "{% include 'b.html' %} content {% import 'c.html'%}"
    graph = build_graph(tpl)
    assert '__main__' in graph
    assert graph['__main__'] == {'b.html', 'c.html'}

def test_build_graph_multi():
    templates = {
        'a': "{% include 'b' %}",
        'b': '{% import "c" %}',
        'c': 'no deps'
    }
    graph = build_graph(None, templates)
    assert graph['a'] == {'b'}
    assert graph['b'] == {'c'}
    assert graph['c'] == set()

def test_render_expr_basic():
    assert render_expr('a + b', {'a': 1, 'b': 2}) == 3

def test_render_expr_sandbox():
    enable_sandbox()
    with pytest.raises(Exception):
        render_expr('__import__("os").system("echo hi")', {})

def test_if_block():
    then = "T"
    elifs = [(False, "E1"), (True, "E2")]
    else_ = "EL"
    assert if_block(True, then, elifs, else_) == then
    assert if_block(False, then, elifs, else_) == "E2"
    assert if_block(False, then, [(False, "E")], else_) == else_

def test_stream_render():
    tpl = "Hello {{ name }}!"
    res = list(stream_render(tpl, {'name': 'World'}))
    assert res == ['Hello ', 'World', '!']

def test_assert_render_success():
    tpl = "{{ x }}+{{ y }}"
    assert_render(tpl, {'x': 1, 'y': 2}, "1+2")

def test_assert_render_failure():
    tpl = "{{ x }}+{{ y }}"
    with pytest.raises(AssertionError):
        assert_render(tpl, {'x': 1, 'y': 3}, "1+2")

def test_profile_render():
    tpl = "A {{ x }} B"
    prof = profile_render(tpl, {'x': 42})
    assert set(prof.keys()) == {'parse', 'compile', 'render', 'result'}
    assert prof['result'] == "A 42 B"
    assert prof['parse'] >= 0

def test_precompile_caching():
    _cache.clear()
    code1 = precompile("tpl")
    code2 = precompile("tpl")
    assert code1 is code2
