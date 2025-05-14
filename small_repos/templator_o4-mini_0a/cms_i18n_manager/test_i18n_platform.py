import os
import tempfile
import threading
import asyncio
import pytest
import yaml
from i18n_platform import (
    auto_reload, auto_reload_enabled,
    define_macro, macros,
    precompile_templates, compiled_templates,
    set_output_mode, output_mode,
    url_encode, url_decode,
    querystring,
    to_json, from_json,
    to_yaml, from_yaml,
    trim_whitespace,
    render_threadsafe, render_async,
    set_locale, current_locale,
    trans,
    render_to_string, render_to_file
)

def test_auto_reload_toggle():
    auto_reload(True)
    assert auto_reload_enabled is True
    auto_reload(False)
    assert auto_reload_enabled is False

def test_define_and_use_macro():
    def hello(name): return f"Hello, {name}!"
    define_macro('hello', hello)
    assert 'hello' in macros
    assert macros['hello']('World') == "Hello, World!"

def test_precompile_templates(tmp_path):
    d = tmp_path / "tpl"
    d.mkdir()
    f1 = d / "a.tmpl"
    f2 = d / "b.txt"
    f1.write_text("Content A", encoding='utf-8')
    f2.write_text("Should skip", encoding='utf-8')
    result = precompile_templates(str(d), 'fr')
    # Only a.tmpl should be compiled
    assert any('a.tmpl' in k for k in result)
    key = (str(d), 'fr')
    assert key in compiled_templates

def test_set_output_mode_and_rendering():
    set_output_mode('escape')
    assert output_mode == 'escape'
    s = render_to_string("<div>{value}</div>", {'value': '<test>'})
    assert s == "<div>&lt;test&gt;</div>"
    set_output_mode('raw')
    assert output_mode == 'raw'
    s2 = render_to_string("<div>{value}</div>", {'value': '<raw>'})
    assert s2 == "<div><raw></div>"
    with pytest.raises(ValueError):
        set_output_mode('invalid')

def test_url_encode_decode_and_querystring():
    original = "a b+c"
    encoded = url_encode(original)
    assert '+' in encoded or '%2B' in encoded
    decoded = url_decode(encoded)
    assert decoded == original
    url = "http://example.com/path"
    qs = querystring(url, lang='en', version=2)
    assert 'lang=en' in qs and 'version=2' in qs

def test_json_yaml_conversion():
    obj = {'a': 1, 'b': [1,2,3]}
    js = to_json(obj)
    back = from_json(js)
    assert back == obj
    y = to_yaml(obj)
    back2 = from_yaml(y)
    assert back2 == obj

def test_trim_whitespace():
    s = "  hello \n"
    assert trim_whitespace(s, 'rtl') == "hello"
    v = "v e r t\ni c a l"
    assert trim_whitespace(v, 'vertical') == "vertical"
    with pytest.raises(ValueError):
        trim_whitespace(s, 'unknown')

def test_render_threadsafe():
    template = "Value: {x}"
    results = []
    def worker(i):
        res = render_threadsafe(template, {'x': i})
        results.append(res)
    threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
    for t in threads: t.start()
    for t in threads: t.join()
    assert sorted(results) == [f"Value: {i}" for i in range(5)]

def test_render_async_loop():
    template = "Hi {name}"
    async def run():
        return await render_async(template, {'name': 'Async'})
    res = asyncio.run(run())
    assert res == "Hi Async"

def test_set_locale_and_trans():
    set_locale('de')
    assert current_locale == 'de'
    assert trans("one|many", count=1) == "one"
    assert trans("one|many", count=5) == "many"
    assert trans("just text") == "just text"

def test_render_to_string_and_file(tmp_path):
    tpl = "User: {user}"
    out = render_to_string(tpl, {'user': 'Tester'})
    assert out == "User: Tester"
    p = tmp_path / "out.html"
    path = render_to_file(tpl, {'user': 'File'}, str(p))
    assert os.path.exists(path)
    assert open(path, 'r', encoding='utf-8').read() == "User: File"
