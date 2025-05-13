import pytest
from templating_engine import *

def test_safe_eval_valid():
    assert safe_eval("1") == 1
    assert safe_eval("[1, 2, 3]") == [1, 2, 3]

def test_safe_eval_invalid():
    with pytest.raises(ValueError):
        safe_eval("__import__('os').system('ls')")

def test_render_stream():
    template = "Hello {name}\nBye {name}"
    result = ''.join(render_stream(template, {'name': 'World'}))
    assert result == "Hello World\nBye World"

def test_scoped_context():
    ctx = {'a': 1}
    with scoped_context(ctx) as c:
        c['a'] = 2
        c['b'] = 3
    assert ctx == {'a': 1}

def test_json_yaml():
    data = {'x': 1}
    js = to_json(data)
    assert from_json(js) == data
    yml = to_yaml(data)
    assert from_yaml(yml)['x'] == 1

def test_autoescape_and_raw():
    s = "<script>"
    assert autoescape(s) == "&lt;script&gt;"
    r = raw("<b>")
    assert isinstance(r, RawString)
    assert autoescape(r) == "<b>"

def test_trim_tags():
    assert trim_tags("  hello  ") == "hello"

def test_define_macro_and_macros_store():
    @define_macro('test')
    def mym():
        return "ok"
    from templating_engine import _macros
    assert 'test' in _macros
    assert _macros['test']() == "ok"

def test_set_delimiters():
    set_delimiters('<<', '>>', '<%', '%>')
    from templating_engine import _delims
    assert _delims['var_start'] == '<<'
    assert _delims['var_end'] == '>>'
    assert _delims['block_start'] == '<%'
    assert _delims['block_end'] == '%>'

def test_basic_math_and_even_odd():
    assert add(2)(3) == 5
    assert sub(5)(2) == 3
    assert mul(3)(4) == 12
    assert div(8)(2) == 4
    assert is_even(4) and not is_even(3)
    assert is_odd(3) and not is_odd(4)

def test_report_error():
    @report_error
    def f():
        raise ValueError("oops")
    with pytest.raises(RuntimeError) as excinfo:
        f()
    assert "Error in f" in str(excinfo.value)
