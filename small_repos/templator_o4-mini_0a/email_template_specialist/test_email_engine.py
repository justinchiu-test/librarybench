import os
import threading
import asyncio
import json
import yaml
import pytest
from email_engine.engine import EmailTemplateEngine

def test_url_encode_decode():
    engine = EmailTemplateEngine(template_dir='.')
    encoded = engine.url_encode('a b&c')
    assert encoded == 'a+b%26c'
    decoded = engine.url_decode(encoded)
    assert decoded == 'a b&c'

def test_querystring_direct_and_pipe():
    engine = EmailTemplateEngine(template_dir='.')
    qs = engine.querystring(a='1', b='2')
    assert qs in ('a=1&b=2', 'b=2&a=1')
    qs2 = engine.querystring({'x':'y','z':'w'})
    parts = qs2.split('&')
    assert set(parts) == set(['x=y','z=w'])
    # test filter in template
    tpl = engine.env.from_string("{{ params|querystring }}")
    out = tpl.render(params={'foo':'bar','baz':'qux'})
    parts = out.split('&')
    assert set(parts) == set(['foo=bar','baz=qux'])

def test_json_filters():
    engine = EmailTemplateEngine(template_dir='.')
    data = {'a':1, 'b':2}
    s = engine.to_json(data)
    assert json.loads(s) == data
    assert engine.from_json(s) == data
    tpl = engine.env.from_string("JSON: {{ data|to_json }}")
    assert tpl.render(data=data) == "JSON: " + json.dumps(data)

def test_yaml_filters():
    engine = EmailTemplateEngine(template_dir='.')
    data = {'a':1, 'b':2}
    y = engine.to_yaml(data)
    assert yaml.safe_load(y) == data
    assert engine.from_yaml(y) == data
    tpl = engine.env.from_string("YAML: {{ data|to_yaml }}")
    assert yaml.safe_load(tpl.render(data=data)) == data

def test_trim_whitespace():
    engine = EmailTemplateEngine(template_dir='.')
    inp = "Line1\n\n  \nLine2\n\nLine3\n"
    out = engine.trim_whitespace(inp)
    assert '\n\n' not in out
    assert out.startswith("Line1")
    assert "Line2" in out
    assert out.endswith("Line3")

def test_locale_and_trans():
    engine = EmailTemplateEngine(template_dir='.')
    assert engine.trans("Hello") == "[en]Hello"
    engine.set_locale('fr')
    assert engine.trans("Bonjour") == "[fr]Bonjour"

def test_define_macro():
    engine = EmailTemplateEngine(template_dir='.')
    engine.define_macro('ftr', '<footer>{{ kwargs["msg"] }}</footer>')
    tpl = engine.env.from_string("{{ ftr(msg='Bye') }}")
    assert tpl.render() == "<footer>Bye</footer>"

def test_output_mode_escape(tmp_path):
    # create simple template directory
    tpl_dir = tmp_path / "tpl"
    tpl_dir.mkdir()
    tpl_file = tpl_dir / "test.html"
    tpl_file.write_text("{{ content }}")
    engine = EmailTemplateEngine(template_dir=str(tpl_dir))
    # html mode (default)
    engine.set_output_mode('html')
    res = engine.render_to_string('test.html', {'content':'<b>bold</b>'})
    assert '&lt;b&gt;bold&lt;/b&gt;' in res
    # raw mode
    engine.set_output_mode('raw')
    res2 = engine.render_to_string('test.html', {'content':'<b>bold</b>'})
    assert '<b>bold</b>' in res2

def test_render_to_string_and_file(tmp_path):
    tpl_dir = tmp_path / "tpl2"
    tpl_dir.mkdir()
    tpl = tpl_dir / "hello.html"
    tpl.write_text("Hello {{ name }}")
    engine = EmailTemplateEngine(template_dir=str(tpl_dir))
    out = engine.render_to_string('hello.html', {'name':'World'})
    assert out == "Hello World"
    # to file
    out_path = tmp_path / "out.html"
    returned = engine.render_to_file('hello.html', {'name':'Tester'}, str(out_path))
    assert returned == str(out_path)
    assert out_path.read_text() == "Hello Tester"

def test_render_threadsafe_concurrent(tmp_path):
    tpl_dir = tmp_path / "tcon"
    tpl_dir.mkdir()
    tpl = tpl_dir / "cnt.html"
    tpl.write_text("Count: {{ i }}")
    engine = EmailTemplateEngine(template_dir=str(tpl_dir))
    results = []
    def job(i):
        r = engine.render_threadsafe('cnt.html', {'i':i})
        results.append(r)
    threads = [threading.Thread(target=job, args=(i,)) for i in range(5)]
    for t in threads: t.start()
    for t in threads: t.join()
    expected = {f"Count: {i}" for i in range(5)}
    assert set(results) == expected

@pytest.mark.asyncio
async def test_render_async(tmp_path):
    tpl_dir = tmp_path / "tasync"
    tpl_dir.mkdir()
    tpl = tpl_dir / "async.html"
    tpl.write_text("Async {{ x }}")
    engine = EmailTemplateEngine(template_dir=str(tpl_dir))
    res = await engine.render_async('async.html', {'x':'Test'})
    assert res == "Async Test"

def test_auto_reload_flag():
    engine = EmailTemplateEngine(template_dir='.')
    assert getattr(engine.env, 'auto_reload', True) is True
    engine.auto_reload(False)
    assert engine.env.auto_reload is False
    engine.auto_reload(True)
    assert engine.env.auto_reload is True

def test_precompile_templates(tmp_path):
    tpl_dir = tmp_path / "tpls"
    tpl_dir.mkdir()
    (tpl_dir / "a.html").write_text("A {{ v }}")
    (tpl_dir / "b.html").write_text("B {{ v }}")
    engine = EmailTemplateEngine(template_dir=str(tpl_dir))
    out_dir = tmp_path / "compiled"
    engine.precompile_templates(str(out_dir))
    files = os.listdir(str(out_dir))
    # Expect compiled Python files for each template
    assert any(f.startswith("a.html") and f.endswith(".py") for f in files)
    assert any(f.startswith("b.html") and f.endswith(".py") for f in files)
