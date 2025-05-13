import pytest
import time
from safe_template import SafeTemplateEngine
from markupsafe import Markup

class Dummy:
    def __init__(self):
        self.child = {'key': 'value'}
        self.value = 123

def test_enable_sandbox_mode_blocks_import():
    engine = SafeTemplateEngine()
    engine.enable_sandbox_mode()
    with pytest.raises(Exception):
        list(engine.render_stream("{{ __import__('os').system('echo hi') }}"))

def test_include_returns_markup():
    engine = SafeTemplateEngine()
    snippet = "<p>Policy</p>"
    inc = engine.include(snippet)
    assert isinstance(inc, Markup)
    assert str(inc) == snippet

def test_cache_template_returns_same_object():
    engine = SafeTemplateEngine()
    tpl1 = engine.cache_template("Hello {{name}}")
    tpl2 = engine.cache_template("Hello {{name}}")
    assert tpl1 is tpl2

def test_render_stream_yields_chunks():
    engine = SafeTemplateEngine()
    snippet = "{% for i in [1,2,3] %}{{i}}-{% endfor %}"
    chunks = list(engine.render_stream(snippet))
    assert ''.join(chunks) == "1-2-3-"

def test_escape_html():
    engine = SafeTemplateEngine()
    raw = '<div class="x"> & </div>'
    escaped = engine.escape_html(raw)
    assert escaped == '&lt;div class=&quot;x&quot;&gt; &amp; &lt;/div&gt;'

def test_escape_json():
    engine = SafeTemplateEngine()
    data = {'a': 1, 'b': "text"}
    j = engine.escape_json(data)
    assert j == '{"a": 1, "b": "text"}'

def test_escape_shell():
    engine = SafeTemplateEngine()
    raw = "it's dangerous"
    shell = engine.escape_shell(raw)
    assert shell.startswith("'") and shell.endswith("'")
    assert "it's dangerous".replace("'", "'\"'\"'") in shell

def test_dot_lookup_dict_and_object():
    engine = SafeTemplateEngine()
    ctx = {'user': {'meta': {'roles': ['admin']}}}
    assert engine.dot_lookup(ctx, 'user.meta.roles') == ['admin']
    ctx2 = {'d': Dummy()}
    assert engine.dot_lookup(ctx2, 'd.child.key') == 'value'
    assert engine.dot_lookup(ctx2, 'd.value') == 123
    assert engine.dot_lookup(ctx2, 'd.missing') is None

def test_minify_removes_comments_and_whitespace():
    engine = SafeTemplateEngine()
    text = """
    <!-- comment -->
    <script>
    // line comment
    var x = 1; /* block comment */
    </script>
    """
    minified = engine.minify(text)
    assert '<script> var x = 1; </script>' in minified

def test_default_filter():
    engine = SafeTemplateEngine()
    assert engine.default_filter('', 'def') == 'def'
    assert engine.default_filter(None, 'def') == 'def'
    assert engine.default_filter('ok', 'def') == 'ok'
    assert engine.default_filter([1], 'def') == [1]

def test_add_filter_and_use_in_template():
    engine = SafeTemplateEngine()
    def shout(s):
        return str(s).upper() + '!'
    engine.add_filter('shout', shout)
    result = engine.env.from_string("{{ 'hi'|shout }}").render()
    assert result == 'HI!'

def test_profile_render_timings_and_output():
    engine = SafeTemplateEngine()
    start = time.time()
    prof = engine.profile_render("Hello {{ name }}", {'name': 'Alice'})
    end = time.time()
    assert 'parse_time' in prof and 'compile_time' in prof and 'render_time' in prof
    assert prof['output'] == 'Hello Alice'
    total = prof['parse_time'] + prof['compile_time'] + prof['render_time']
    # total should be non-negative and less than wall time
    assert 0 <= prof['parse_time'] <= end - start
    assert 0 <= prof['compile_time'] <= end - start
    assert 0 <= prof['render_time'] <= end - start
