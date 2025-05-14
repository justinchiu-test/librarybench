import pytest
import functools
import getpass
from cli_toolkit import (
    ask_text, branch_flow, load_choices_async, input_line_fallback,
    review_submission, ask_password, select_choices,
    set_renderer_theme, register_on_change, trigger_change,
    format_errors
)

def test_ask_text_valid(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda prompt='': "hello")
    result = ask_text("Enter name", min_length=3, max_length=10, placeholder="e.g. users")
    assert result == "hello"

def test_ask_text_invalid(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda prompt='': "hi")
    with pytest.raises(ValueError) as exc:
        ask_text("Enter name", min_length=3, max_length=10)
    assert "ERROR:" in str(exc.value)

def test_branch_flow_valid():
    flows = {'a': lambda: 'A', 'b': lambda: 'B'}
    assert branch_flow('a', flows) == 'A'
    assert branch_flow('b', flows) == 'B'

def test_branch_flow_invalid():
    flows = {'x': lambda: 1}
    with pytest.raises(ValueError) as exc:
        branch_flow('y', flows)
    assert "Invalid choice" in str(exc.value)

def test_load_choices_async_caching():
    calls = {'count': 0}
    def loader(x):
        calls['count'] += 1
        return [x]
    res1 = load_choices_async(loader, 5)
    res2 = load_choices_async(loader, 5)
    assert res1 == [5]
    assert res1 is res2
    assert calls['count'] == 1

def test_input_line_fallback_context():
    with input_line_fallback() as fb:
        assert hasattr(fb, 'mode')
        assert fb.mode == 'fallback'
        assert repr(fb).startswith("<FallbackCLI")

def test_review_submission():
    data = {'a': 1, 'b': 2}
    out = review_submission(data)
    assert out == data
    assert out is not data  # returns a new dict

def test_ask_password(monkeypatch):
    monkeypatch.setattr(getpass, 'getpass', lambda prompt='': "secret")
    pwd = ask_password("Enter pass")
    assert pwd == "secret"

def test_select_choices_valid(monkeypatch):
    options = ['x', 'y', 'z']
    monkeypatch.setattr('builtins.input', lambda prompt='': "0,2")
    sel = select_choices(options)
    assert sel == ['x', 'z']

def test_select_choices_default(monkeypatch):
    options = ['a', 'b']
    monkeypatch.setattr('builtins.input', lambda prompt='': "")
    sel = select_choices(options, default=[1])
    assert sel == ['b']

def test_select_choices_invalid(monkeypatch):
    options = ['a']
    monkeypatch.setattr('builtins.input', lambda prompt='': "5")
    with pytest.raises(ValueError):
        select_choices(options)

def test_set_renderer_theme_valid():
    assert set_renderer_theme("minimal") == "minimal"
    assert set_renderer_theme("high-contrast") == "high-contrast"

def test_set_renderer_theme_invalid():
    with pytest.raises(ValueError) as exc:
        set_renderer_theme("dark")
    assert "Unknown theme" in str(exc.value)

def test_register_on_change_and_trigger():
    result = {}
    def cb(val):
        result['v'] = val * 2
    register_on_change('field1', cb)
    trigger_change('field1', 3)
    assert result['v'] == 6

def test_format_errors_colors():
    msg = "oops"
    out = format_errors(msg)
    assert out.startswith("\033[91m")
    assert "oops" in out
    assert out.endswith("\033[0m")
