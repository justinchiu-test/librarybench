import pytest
import ast
from report_engine import (
    safe_eval, render_stream, scoped_context, to_json, from_json,
    to_yaml, from_yaml, report_error, autoescape, raw, trim_tags,
    macros, set_delimiters, bar_chart, line_chart,
    add, sub, mul, div, is_even, is_odd, SafeString
)

def test_safe_eval_valid_literals():
    assert safe_eval("'hello'") == "hello"
    assert safe_eval("123") == 123
    assert safe_eval("[1, 2, 3]") == [1, 2, 3]
    assert safe_eval("{'a': 1}") == {'a': 1}
    assert safe_eval("(-5)") == -5

def test_safe_eval_invalid():
    with pytest.raises(ValueError):
        safe_eval("__import__('os')")
    with pytest.raises(ValueError):
        safe_eval("open('file')")
    with pytest.raises(ValueError):
        safe_eval("a + b")

def test_render_stream_string():
    s = "abcdefghijklmnopqrstuvwxyz"
    chunks = list(render_stream(s, chunk_size=5))
    assert chunks == ["abcde", "fghij", "klmno", "pqrst", "uvwxy", "z"]

def test_render_stream_list():
    data = [1,2,3,4,5,6,7]
    chunks = list(render_stream(data, chunk_size=3))
    assert chunks == [[1,2,3], [4,5,6], [7]]

def test_render_stream_invalid():
    with pytest.raises(TypeError):
        list(render_stream(123, chunk_size=2))

def test_scoped_context_isolation():
    ctx = {'a': 1}
    with scoped_context(ctx) as c:
        c['b'] = 2
        assert c['a'] == 1
        assert c['b'] == 2
    assert 'b' not in ctx
    assert ctx == {'a': 1}

def test_json_yaml_roundtrip():
    data = {'x': [1,2,3], 'y': {'z': 'test'}}
    js = to_json(data)
    assert isinstance(js, str)
    assert from_json(js) == data
    ys = to_yaml(data)
    assert isinstance(ys, str)
    loaded = from_yaml(ys)
    assert loaded == data

def test_report_error_format():
    err = ValueError("oops")
    msg = report_error(err, "line1")
    assert "ValueError" in msg
    assert "oops" in msg
    assert "line1" in msg

def test_autoescape_and_raw_and_trim():
    unsafe = "<div> & text"
    esc = autoescape(unsafe)
    assert "&lt;div&gt;" in esc
    r = raw(unsafe)
    assert isinstance(r, SafeString)
    assert autoescape(r) == r
    trimmed = "hello>   <world"
    assert trim_tags(trimmed) == "hello><world"

def test_macros_registration_and_delimiters():
    assert 'bar_chart' in macros
    assert 'line_chart' in macros
    set_delimiters("<<%", "%>>")
    out = bar_chart([1,2,3], color='blue')
    assert isinstance(out, SafeString)
    assert out.startswith("<<%")
    assert out.endswith("%>>")
    out2 = line_chart([4,5], width=400)
    assert "<<% line_chart" in out2

def test_arithmetic():
    assert add(2,3) == 5
    assert sub(5,2) == 3
    assert mul(3,4) == 12
    assert div(10,2) == 5

def test_even_odd():
    assert is_even(2)
    assert not is_even(3)
    assert is_odd(3)
    assert not is_odd(2)
