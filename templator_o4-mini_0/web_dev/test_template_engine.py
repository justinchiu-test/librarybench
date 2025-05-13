import threading
import asyncio
import io
import pytest
import yaml
from template_engine import TemplateEngine

@pytest.fixture
def engine():
    return TemplateEngine()

def test_auto_reload(engine):
    assert not engine.auto_reload
    engine.set_auto_reload(True)
    assert engine.auto_reload
    engine.set_auto_reload(False)
    assert not engine.auto_reload

def test_define_macro(engine):
    engine.define_macro('card', ['title', 'body'], '<div>{{ title }}: {{ body }}</div>')
    assert 'card' in engine.macros
    macro = engine.macros['card']
    assert macro['args'] == ['title', 'body']
    assert 'body' in macro['content']

def test_precompile_templates(engine):
    engine.templates['home'] = "<h1>Home</h1>"
    engine.templates['about'] = "<p>About</p>"
    engine.precompile_templates()
    assert 'home' in engine._precompiled
    assert 'about' in engine._precompiled
    for code in engine._precompiled.values():
        assert hasattr(code, 'co_code')

def test_set_output_mode(engine):
    assert engine.output_mode == 'escape'
    engine.set_output_mode('raw')
    assert engine.output_mode == 'raw'
    with pytest.raises(ValueError):
        engine.set_output_mode('invalid')

def test_url_encode_decode(engine):
    original = "a b/c?d=e&f"
    encoded = engine.url_encode(original)
    assert '%' in encoded
    decoded = engine.url_decode(encoded)
    assert decoded == original

def test_querystring(engine):
    url = "https://example.com/search"
    params = {'q': 'test', 'page': 2}
    full = engine.querystring(url, params)
    assert 'q=test' in full and 'page=2' in full
    # existing query
    url2 = "https://example.com/search?x=1"
    full2 = engine.querystring(url2, {'y': '2'})
    assert 'x=1' in full2 and 'y=2' in full2

def test_json_filters(engine):
    obj = {'a': 1, 'b': [1,2,3]}
    s = engine.to_json(obj)
    assert isinstance(s, str)
    back = engine.from_json(s)
    assert back == obj

def test_yaml_filters(engine):
    obj = {'a': 1, 'b': [1,2,3]}
    s = engine.to_yaml(obj)
    assert isinstance(s, str)
    back = engine.from_yaml(s)
    assert back == obj

def test_trim_whitespace(engine):
    s = "Hello {{- name -}} !"
    trimmed = engine.trim_whitespace(s)
    assert trimmed == "Hello{{- name -}}!"

def test_render_to_string_basic(engine):
    engine.templates['greet'] = "Hi, {{ name }}!"
    out = engine.render_to_string('greet', {'name': 'Alice'})
    assert out == "Hi, Alice!"

def test_render_to_string_trimmed(engine):
    engine.templates['trim'] = "A {{- key -}} B"
    out = engine.render_to_string('trim', {'key': 'X'})
    assert out == "A{{- key -}}B".replace('key', 'X')

def test_translations(engine):
    engine.templates['t'] = '{% trans "Hello" %}, {{ user }}'
    engine.set_locale('fr_FR')
    engine.add_translations('fr_FR', {'Hello': 'Bonjour'})
    out = engine.render_to_string('t', {'user': 'Jean'})
    assert out == "Bonjour, Jean"

def test_render_to_file_strpath(tmp_path, engine):
    engine.templates['file'] = "Data: {{ x }}"
    path = tmp_path / "out.txt"
    engine.render_to_file('file', {'x': 42}, str(path))
    content = path.read_text(encoding='utf-8')
    assert "42" in content

def test_render_to_file_fileobj(engine):
    engine.templates['file2'] = "Value={{ v }}"
    buf = io.StringIO()
    engine.render_to_file('file2', {'v': 'OK'}, buf)
    assert buf.getvalue() == "Value=OK"

def test_render_threadsafe(engine):
    engine.templates['thr'] = "User: {{ u }}"
    results = []
    def worker(u):
        results.append(engine.render_threadsafe('thr', {'u': u}))
    threads = [threading.Thread(target=worker, args=(i,)) for i in range(5)]
    for t in threads: t.start()
    for t in threads: t.join()
    assert sorted(results) == [f"User: {i}" for i in range(5)]

@pytest.mark.asyncio
async def test_render_async(engine):
    engine.templates['async'] = "A={{ a }}"
    out = await engine.render_async('async', {'a': 100})
    assert out == "A=100"
