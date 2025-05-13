import pytest
import yaml
import json
from template_engine import (
    safe_eval, scoped_context, render_stream, to_json, from_json,
    to_yaml, from_yaml, report_error, TemplateError, autoescape, raw,
    trim_tags, define_macro, call_macro, set_delimiters,
    add, sub, mul, div, is_even, is_odd
)

def test_safe_eval_literals():
    assert safe_eval("1+2*3") == 7
    assert safe_eval("-5") == -5
    assert safe_eval("2.5+0.5") == 3.0
    assert safe_eval("'a'+'b'") == "ab"

def test_safe_eval_disallowed():
    with pytest.raises(ValueError):
        safe_eval("__import__('os').system('rm -rf /')")

def test_scoped_context():
    ctx = {'a':1,'b':2}
    with scoped_context(ctx, a=10, c=3) as subctx:
        assert subctx['a'] == 10
        assert subctx['b'] == 2
        assert subctx['c'] == 3
    assert ctx['a'] == 1
    assert 'c' not in ctx

def test_render_stream_default_delimiters():
    template = "Hello {{name}}\nBye {{name}}"
    set_delimiters("{{", "}}")
    result = ''.join(render_stream(template, {'name':'World'}))
    assert result == "Hello World\nBye World"

def test_set_delimiters_affect_render():
    set_delimiters("<<", ">>")
    template = "Num <<n>>"
    out = ''.join(render_stream(template, {'n':42}))
    assert out == "Num 42"

def test_json_functions():
    obj = {'x':1,'y':[2,3]}
    s = to_json(obj)
    assert isinstance(s, str)
    assert from_json(s) == obj

def test_yaml_functions():
    obj = {'a':1,'b':[2,3]}
    y = to_yaml(obj)
    assert isinstance(y, str)
    assert from_yaml(y) == obj

def test_report_error():
    with pytest.raises(TemplateError) as excinfo:
        report_error(Exception("fail"), "file.txt", 10)
    msg = str(excinfo.value)
    assert "file.txt:10: fail" in msg

def test_autoescape_and_raw():
    s = '<tag attr="val">&text</tag>'
    esc = autoescape(s)
    assert '&lt;tag' in esc and '&gt;' in esc and '&amp;text' in esc
    assert raw(s) == s

def test_trim_tags():
    assert trim_tags("  hello  ") == "hello"

def test_macros():
    @define_macro('greet')
    def greet(name):
        return f"Hi {name}"
    assert call_macro('greet', 'Alice') == "Hi Alice"
    with pytest.raises(TemplateError):
        call_macro('nonexistent')

def test_arithmetic_and_predicates():
    assert add(2,3) == 5
    assert sub(5,2) == 3
    assert mul(3,4) == 12
    assert div(10,2) == 5
    assert is_even(2)
    assert not is_even(3)
    assert is_odd(3)
    assert not is_odd(2)
