import threading
import asyncio
import inspect
import os
import tempfile
import time
import pytest
from dashboard.templating import (
    auto_reload, define_macro, precompile_templates, set_output_mode,
    url_encode, url_decode, querystring, to_json, from_json,
    to_yaml, from_yaml, trim_whitespace, render_threadsafe,
    render_async, set_locale, trans, render_to_string, render_to_file,
    ReloadMonitor
)

def test_url_encode_decode():
    params = {'a': '1', 'b': 'x y', 'c': 3}
    encoded = url_encode(params)
    assert 'a=1' in encoded
    assert 'b=x+y' in encoded
    decoded = url_decode(encoded)
    assert decoded == {'a': '1', 'b': 'x y', 'c': '3'}
    # string input
    single = "hello world"
    enc = url_encode(single)
    assert enc == "hello+world"
    dec = url_decode(enc)
    assert dec == {'hello+world': ''} or isinstance(dec, dict)

def test_querystring():
    base = "http://example.com"
    qs = querystring(base, {'p': 'val', 'q': 'a b'})
    assert qs.startswith(base + '?')
    assert 'p=val' in qs and 'q=a+b' in qs
    base2 = "http://ex.com?x=1"
    qs2 = querystring(base2, {'y':2})
    assert qs2.startswith(base2 + '&')
    assert 'y=2' in qs2

def test_json_yaml():
    data = {'x': [1,2,3], 'y': 'test'}
    js = to_json(data)
    assert isinstance(js, str)
    assert from_json(js) == data
    yl = to_yaml(data)
    assert isinstance(yl, str)
    assert from_yaml(yl) == data

def test_trim_whitespace():
    raw = "<div>   \n   <span>Hi</span>   </div>"
    trimmed = trim_whitespace(raw)
    assert '><' in trimmed
    assert not trimmed.startswith(' ')
    assert not trimmed.endswith(' ')

def test_define_macro_and_render():
    def greet():
        return "hello"
    define_macro('greet', greet)
    tpl = "Say {{ greet() }} to device."
    out = render_to_string(tpl)
    assert out == "Say hello to device."
    # test variable
    tpl2 = "Device: {{ name }}"
    out2 = render_to_string(tpl2, {'name': 'Sensor'})
    assert out2 == "Device: Sensor"

def test_set_output_mode():
    set_output_mode('raw')
    with pytest.raises(ValueError):
        set_output_mode('invalid')
    # ensure mode persists internally
    set_output_mode('escape')
    # no direct getter; rely on no exception

def test_precompile_templates():
    templates = {'one': 'tpl1', 'two': 'tpl2'}
    compiled = precompile_templates(templates)
    assert compiled['one'] == 'Compiled:tpl1'
    assert compiled['two'] == 'Compiled:tpl2'

def test_render_threadsafe():
    results = []
    def add(x):
        results.append(x)
        return x
    safe_add = render_threadsafe(add)
    assert hasattr(safe_add, '_lock')
    threads = []
    for i in range(5):
        t = threading.Thread(target=safe_add, args=(i,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    assert sorted(results) == list(range(5))

def test_render_async():
    def greet():
        return "hi"
    async_greet = render_async(greet)
    assert inspect.iscoroutinefunction(async_greet)
    result = asyncio.get_event_loop().run_until_complete(async_greet())
    assert result == "hi"

def test_set_locale_and_trans():
    set_locale('fr')
    # internal, but ensure trans wraps correctly
    text = "Hello"
    wrapped = trans(text)
    assert wrapped.startswith("{% trans %}")
    assert wrapped.endswith("{% endtrans %}")
    assert text in wrapped

def test_render_to_file_and_string(tmp_path):
    tpl = "Value: {{ v }}"
    ctx = {'v': 10}
    s = render_to_string(tpl, ctx)
    assert s == "Value: 10"
    file_path = tmp_path / "out.html"
    ret = render_to_file(tpl, str(file_path), ctx)
    assert ret == str(file_path)
    with open(ret, 'r', encoding='utf-8') as f:
        content = f.read()
    assert content == "Value: 10"

def test_auto_reload_monitor():
    def cb():
        pass
    m = auto_reload('somepath', cb)
    assert isinstance(m, ReloadMonitor)
    assert hasattr(m, 'start') and hasattr(m, 'stop')
