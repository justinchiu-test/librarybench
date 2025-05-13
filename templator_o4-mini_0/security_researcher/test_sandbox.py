import pytest
import sandbox
import json
import yaml

def test_safe_eval_numbers_and_ops():
    assert sandbox.safe_eval("1 + 2") == 3
    assert sandbox.safe_eval("10 - 3") == 7
    assert sandbox.safe_eval("2 * 5") == 10
    assert sandbox.safe_eval("8 / 2") == 4
    assert sandbox.safe_eval("2 ** 3") == 8
    assert sandbox.safe_eval("-5") == -5
    assert sandbox.safe_eval("True and False") is False
    assert sandbox.safe_eval("1 < 2 < 3") is True

def test_safe_eval_literals_and_containers():
    assert sandbox.safe_eval("'hello'") == "hello"
    assert sandbox.safe_eval("[1, 2, 3]") == [1,2,3]
    assert sandbox.safe_eval("(4,5)") == (4,5)
    assert sandbox.safe_eval("{'a':1}") == {'a':1}
    assert sandbox.safe_eval("{1,2,3}") == {1,2,3}
    assert sandbox.safe_eval("None") is None

def test_safe_eval_disallowed():
    with pytest.raises(ValueError):
        sandbox.safe_eval("__import__('os').system('ls')")
    with pytest.raises(ValueError):
        sandbox.safe_eval("().__class__")
    with pytest.raises(ValueError):
        sandbox.safe_eval("open('file')")

def test_scoped_context_mutation():
    outer = {'x': [1,2], 'y': 10}
    with sandbox.scoped_context(outer) as ctx:
        ctx['x'].append(3)
        ctx['y'] = 20
    # outer must remain unchanged
    assert outer == {'x':[1,2], 'y':10}

def test_render_stream_basic():
    data = "abcdef"
    chunks = list(sandbox.render_stream(data, chunk_size=2))
    assert chunks == [b"ab", b"cd", b"ef"]

def test_json_roundtrip():
    obj = {'a':1, 'b':[1,2,3]}
    j = sandbox.to_json(obj)
    assert isinstance(j, str)
    assert sandbox.from_json(j) == obj

def test_yaml_roundtrip():
    obj = {'a':1, 'b':[1,2,3]}
    y = sandbox.to_yaml(obj)
    assert isinstance(y, str)
    assert sandbox.from_yaml(y) == obj

def test_report_error_includes_snippet():
    code = "a=1\nb=2\nc=1/0\n"
    try:
        exec(code)
    except Exception as e:
        report = sandbox.report_error(code, e)
        assert "ZeroDivisionError" in report
        assert "1: a=1" in report
        assert "3: c=1/0" in report

def test_autoescape_and_raw():
    text = "<script>alert</script>"
    with sandbox.autoescape():
        escaped = sandbox.escape(text)
        assert "&lt;script&gt;alert&lt;/script&gt;" == escaped
    # default escape on
    escaped2 = sandbox.escape(text)
    assert "&lt;script&gt;alert&lt;/script&gt;" == escaped2
    # raw context
    with sandbox.raw():
        rawtext = sandbox.escape(text)
        assert rawtext == text
    # after raw, escape back on
    assert sandbox.escape(text).startswith("&lt;")

def test_trim_tags():
    inp = "<div>   <span> text </span>   </div>"
    out = sandbox.trim_tags(inp)
    assert out == "<div><span> text </span></div>"

def test_macros_and_delimiters():
    sandbox.MACROS.clear()
    sandbox.set_delimiters("{{", "}}")
    sandbox.define_macro("foo", "bar")
    txt = "Value: {{foo}}"
    assert sandbox.expand_macros(txt) == "Value: bar"
    # change delimiters
    sandbox.set_delimiters("<%", "%>")
    txt2 = "Value: <%foo%>"
    assert sandbox.expand_macros(txt2) == "Value: bar"

def test_arithmetic_helpers_and_conditions():
    assert sandbox.add(2,3) == 5
    assert sandbox.sub(5,2) == 3
    assert sandbox.mul(3,4) == 12
    assert sandbox.div(8,2) == 4
    assert sandbox.is_even(4) is True
    assert sandbox.is_even(5) is False
    assert sandbox.is_odd(3) is True
    assert sandbox.is_odd(2) is False

def test_from_json_invalid():
    with pytest.raises(json.JSONDecodeError):
        sandbox.from_json("not a json")

def test_from_yaml_invalid():
    with pytest.raises(yaml.YAMLError):
        sandbox.from_yaml("::not yaml::")
