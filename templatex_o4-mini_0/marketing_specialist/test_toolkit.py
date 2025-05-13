import os
import time
import pytest
from toolkit import (
    enable_sandbox_mode, include, cache_template, render_stream,
    escape_html, escape_shell, escape_json, dot_lookup,
    minify_html, default_filter, add_filter,
    profile_render, get_cache, clear_cache,
    get_profiles, clear_profiles
)

def test_escape_html():
    raw = '<script>alert("x")</script>'
    assert escape_html(raw) == '&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;'

def test_escape_shell():
    raw = "O'Reilly"
    esc = escape_shell(raw)
    assert esc.startswith("'") and esc.endswith("'")
    # unescaped content not in output
    assert "O'Reilly" not in esc
    # evaluate stripped quotes
    inner = esc[1:-1].replace("'\"'\"'", "'")
    assert inner == raw

def test_escape_json():
    data = {"key": "value", "num": 1}
    j = escape_json(data)
    assert isinstance(j, str)
    parsed = __import__('json').loads(j)
    assert parsed == data

def test_dot_lookup_dict_and_obj():
    ctx = {'user': {'first_name': 'Alice'}}
    assert dot_lookup(ctx, 'user.first_name') == 'Alice'
    class Obj: pass
    o = Obj()
    o.name = 'Bob'
    ctx2 = {'o': o}
    assert dot_lookup(ctx2, 'o.name') == 'Bob'
    assert dot_lookup(ctx2, 'o.missing') is None
    assert dot_lookup(ctx2, 'x.y') is None

def test_minify_html():
    html_in = """
    <div>
        <!-- comment -->
        <p>Text    here</p>
    </div>
    """
    out = minify_html(html_in)
    assert '<!--' not in out
    assert '  ' not in out
    assert out.startswith('<div>')
    assert out.endswith('</div>')

def test_default_filter():
    assert default_filter(None, 'X') == 'X'
    assert default_filter('', 'Y') == 'Y'
    assert default_filter('Z', 'Y') == 'Z'
    assert default_filter(0, 'Y') == 0

def test_add_filter_and_render_stream(tmp_path):
    # create a template
    tpl = tmp_path / "greet.html"
    tpl.write_text("Hello {{ user.name|shout }}!")
    # add filter
    add_filter('shout', lambda s: s.upper() + '!!!')
    ctx = {'user': {'name': 'test'}}
    # render_stream
    chunks = list(render_stream(str(tpl), ctx))
    output = "".join(chunks)
    assert output == "Hello TEST!!!!"

def test_cache_and_include(tmp_path):
    clear_cache()
    tpl = tmp_path / "foo.html"
    tpl.write_text("Content")
    # include reads from fs
    assert include(str(tpl)) == "Content"
    # cache_template
    cache_template(str(tpl))
    cached = get_cache()
    assert str(tpl) in cached
    # include should return new read, cache used only by cache_template
    tpl.write_text("New")
    assert include(str(tpl)) == "New"

def test_sandbox_mode(tmp_path):
    clear_cache()
    enable_sandbox_mode()
    tpl = tmp_path / "a.html"
    tpl.write_text("X")
    with pytest.raises(RuntimeError):
        include(str(tpl))

def test_render_stream_basic(tmp_path):
    tpl = tmp_path / "basic.html"
    tpl.write_text("A{{x}}B{{y}}C")
    ctx = {'x':1, 'y':2}
    out = "".join(render_stream(str(tpl), ctx))
    assert out == "A1B2C"

def test_profile_render():
    clear_profiles()
    @profile_render('test')
    def fast():
        return "ok"
    @profile_render('test')
    def slow():
        time.sleep(0.01)
        return "done"
    assert fast() == "ok"
    assert slow() == "done"
    prof = get_profiles('test')
    assert len(prof) == 2
    assert prof[0] >= 0
    assert prof[1] >= 0.01

def test_escape_json_with_string():
    s = 'Hello\nWorld'
    j = escape_json(s)
    assert json.loads(j) == s

import json  # for the last test
