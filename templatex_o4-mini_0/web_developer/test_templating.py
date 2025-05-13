import os
import tempfile
import pytest
from templating import TemplateEngine

def test_escape_html():
    engine = TemplateEngine()
    assert engine.escape_html('<div>"&\'</div>') == '&lt;div&gt;&quot;&amp;&#x27;&lt;/div&gt;'

def test_escape_json():
    engine = TemplateEngine()
    assert engine.escape_json({'a': 1}) == '{"a": 1}'

def test_escape_shell():
    engine = TemplateEngine()
    assert engine.escape_shell("foo bar") == "'foo bar'"

def test_dot_lookup():
    engine = TemplateEngine()
    ctx = {'user': {'profile': {'name': 'Alice'}}}
    assert engine.dot_lookup(ctx, 'user.profile.name') == 'Alice'
    assert engine.dot_lookup(ctx, 'user.age') is None

def test_default_filter():
    engine = TemplateEngine()
    assert engine.default_filter(None, 'Guest') == 'Guest'
    assert engine.default_filter('Bob', 'Guest') == 'Bob'

def test_add_filter():
    engine = TemplateEngine()
    engine.add_filter('shout', lambda v: str(v).upper())
    tpl_dir = tempfile.mkdtemp()
    with open(os.path.join(tpl_dir, 'test.tpl'), 'w') as f:
        f.write("Say {{ name|shout }}!")
    engine = TemplateEngine(template_dir=tpl_dir)
    engine.add_filter('shout', lambda v: str(v).upper())
    out = engine.render('test.tpl', {'name': 'hi'})
    assert out == 'Say HI!'

def test_include_and_caching():
    tpl_dir = tempfile.mkdtemp()
    with open(os.path.join(tpl_dir, 'sub.tpl'), 'w') as f:
        f.write("World")
    with open(os.path.join(tpl_dir, 'main.tpl'), 'w') as f:
        f.write("Hello {% include 'sub.tpl' %}!")
    engine = TemplateEngine(template_dir=tpl_dir)
    assert not engine._cache
    out1 = engine.render('main.tpl')
    assert out1 == 'Hello World!'
    # cache should have both templates
    assert 'main.tpl' in engine._cache
    assert 'sub.tpl' in engine._cache
    cache_size = len(engine._cache)
    out2 = engine.render('main.tpl')
    assert out2 == 'Hello World!'
    assert len(engine._cache) == cache_size

def test_render_stream_and_minify():
    tpl_dir = tempfile.mkdtemp()
    with open(os.path.join(tpl_dir, 'p.tpl'), 'w') as f:
        f.write("A   <!-- comment --> B")
    engine = TemplateEngine(template_dir=tpl_dir)
    stream = list(engine.render_stream('p.tpl'))
    assert "A   <!-- comment --> B" in ''.join(stream)
    minified = engine.minify_html('A   <!-- comment --> B')
    assert minified == 'A B'

def test_profile_render():
    tpl_dir = tempfile.mkdtemp()
    with open(os.path.join(tpl_dir, 'x.tpl'), 'w') as f:
        f.write("{{ name }}")
    engine = TemplateEngine(template_dir=tpl_dir)
    res = engine.profile_render('x.tpl', {'name': 'Test'})
    assert 'parse_compile_time' in res
    assert 'render_time' in res
    assert res['output'] == 'Test'

def test_sandbox_mode_flag():
    engine = TemplateEngine()
    assert not engine.enable_sandbox
    engine.enable_sandbox_mode()
    assert engine.enable_sandbox
