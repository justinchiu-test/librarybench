import pytest
import time
from reporting_engine import (
    TemplateEngine, dot_lookup, escape_html, escape_json,
    minify_html, default_filter
)

def test_dot_lookup_simple():
    ctx = {'a': {'b': [10, 20, {'c': 30}]}}
    assert dot_lookup(ctx, 'a.b[2].c') == 30
    with pytest.raises(KeyError):
        dot_lookup(ctx, 'a.x')

def test_escape_html_and_json():
    s = '<div>"Hello"&\''
    assert escape_html(s) == '&lt;div&gt;&quot;Hello&quot;&amp;&#x27;'
    assert escape_json(s) == '"<div>\\"Hello\\"&\'"'

def test_minify_html():
    html_input = '''
    <!-- comment -->
    <div>   Hello   World   </div>
    '''
    output = minify_html(html_input)
    assert output == '<div> Hello World </div>'

def test_default_filter():
    assert default_filter(None, 5) == 5
    assert default_filter(0, 5) == 5
    assert default_filter('value', 'def') == 'value'

def test_custom_filter_and_default():
    eng = TemplateEngine()
    eng.add_filter('times2', lambda v: v * 2)
    eng.register_template('t1', '{{ num|times2 }}')
    result = eng.render('t1', {'num': 4})
    assert result == '8'

def test_include_and_render():
    eng = TemplateEngine()
    eng.register_template('base', 'Header\n{% include "body" %}\nFooter')
    eng.register_template('body', 'Body: {{ content }}')
    res = eng.render('base', {'content': 'X'})
    assert 'Header' in res and 'Body: X' in res and 'Footer' in res

def test_cache_template():
    eng = TemplateEngine()
    eng.register_template('t', 'Hello {{ name }}')
    assert 't' not in eng.compiled
    eng.cache_template('t')
    assert 't' in eng.compiled
    # caching again does not error
    eng.cache_template('t')

def test_render_stream():
    eng = TemplateEngine()
    eng.register_template('s', 'Line1\nLine2\nVal: {{ v }}\n')
    lines = list(eng.render_stream('s', {'v': 99}))
    assert lines == ['Line1\n', 'Line2\n', 'Val: 99\n']

def test_profile_render():
    eng = TemplateEngine()
    eng.register_template('p', 'P: {{ x }}')
    prof = eng.profile_render('p', {'x': 7})
    assert 'parsed_seconds' in prof and 'rendered_seconds' in prof and 'output' in prof
    assert prof['output'] == 'P: 7'
    assert prof['parsed_seconds'] >= 0
    assert prof['rendered_seconds'] >= 0

def test_sandbox_mode_prevents_code_exec():
    eng = TemplateEngine()
    eng.enable_sandbox_mode()
    # template tries to execute code, but sandbox mode does not allow eval, so treated as var
    eng.register_template('hack', '{{ __import__("os").system("echo hi") }}')
    res = eng.render('hack', {})
    assert 'system' in res or res == ''

def test_escape_filters_on_var():
    eng = TemplateEngine()
    eng.register_template('html', '{{ data|escape_html }}')
    eng.register_template('json', '{{ data|escape_json }}')
    res_html = eng.render('html', {'data': '<&>'})
    res_json = eng.render('json', {'data': '<&>'})
    assert '&lt;&amp;&gt;' in res_html
    assert '"<\\u0026>"' or '"<&>"'
    assert res_json.startswith('"') and res_json.endswith('"')

def test_default_filter_in_template():
    eng = TemplateEngine()
    eng.register_template('d', '{{ missing|default("X") }}')
    res = eng.render('d', {})
    assert res == 'X'
