import re
import getpass
import pytest
from cli_form import CLIForm

def test_ask_text_valid(monkeypatch):
    form = CLIForm()
    monkeypatch.setattr('builtins.input', lambda prompt: "cluster1")
    val = form.ask_text("name", "Enter name", min_length=3, max_length=10, pattern=r'^\w+$', placeholder="cluster")
    assert val == "cluster1"
    assert form.answers["name"] == "cluster1"

def test_ask_text_min_length(monkeypatch):
    form = CLIForm()
    monkeypatch.setattr('builtins.input', lambda prompt: "ab")
    with pytest.raises(ValueError):
        form.ask_text("name", "Enter", min_length=3)

def test_ask_text_max_length(monkeypatch):
    form = CLIForm()
    monkeypatch.setattr('builtins.input', lambda prompt: "toolong")
    with pytest.raises(ValueError):
        form.ask_text("name", "Enter", max_length=3)

def test_ask_text_pattern(monkeypatch):
    form = CLIForm()
    monkeypatch.setattr('builtins.input', lambda prompt: "abc")
    with pytest.raises(ValueError):
        form.ask_text("num", "Enter number", pattern=r'^\d+$')

def test_branch_flow_dict():
    form = CLIForm()
    form.answers['provider'] = 'aws'
    flows = {
        'aws': lambda: "AWS FLOW",
        'gcp': lambda: "GCP FLOW"
    }
    res = form.branch_flow(lambda ans: ans.get('provider'), flows)
    assert res == "AWS FLOW"

def test_branch_flow_list():
    form = CLIForm()
    form.answers['ok'] = True
    flows = [
        (lambda ans: not ans.get('ok'), "NO"),
        (lambda ans: ans.get('ok'), "YES")
    ]
    res = form.branch_flow(lambda ans: None, flows)
    assert res == "YES"

def test_load_choices_async_caching():
    form = CLIForm()
    counter = {'count': 0}
    def loader():
        counter['count'] += 1
        return ['a', 'b']
    first = form.load_choices_async('key', loader)
    second = form.load_choices_async('key', loader)
    assert first == ['a', 'b']
    assert second == ['a', 'b']
    assert counter['count'] == 1

def test_input_line_fallback(monkeypatch):
    form = CLIForm()
    monkeypatch.setattr('builtins.input', lambda prompt: "fallback")
    val = form.input_line_fallback("fb", "Prompt")
    assert val == "fallback"
    assert form.answers["fb"] == "fallback"

def test_ask_password_no_meter(monkeypatch):
    form = CLIForm()
    monkeypatch.setattr(getpass, 'getpass', lambda prompt: "secret")
    val = form.ask_password("pw", "Enter PW", strength_meter=False)
    assert val == "secret"
    assert form.answers["pw"] == "secret"

def test_ask_password_with_meter(monkeypatch):
    form = CLIForm()
    monkeypatch.setattr(getpass, 'getpass', lambda prompt: "longsecret")
    val = form.ask_password("pw", "Enter PW", strength_meter=True)
    assert isinstance(val, dict)
    assert val["value"] == "longsecret"
    assert val["strength"] == "strong"
    assert form.answers["pw"] == val

def test_select_choices_single(monkeypatch, capsys):
    form = CLIForm()
    choices = ['one', 'two', 'three']
    monkeypatch.setattr('builtins.input', lambda prompt: "2")
    selected = form.select_choices("sel", "Choose", choices, multi=False)
    assert selected == 'two'
    assert form.answers["sel"] == 'two'

def test_select_choices_multi(monkeypatch, capsys):
    form = CLIForm()
    choices = ['a', 'b', 'c', 'd']
    monkeypatch.setattr('builtins.input', lambda prompt: "1,3")
    selected = form.select_choices("msel", "Choose", choices, multi=True)
    assert selected == ['a', 'c']
    assert form.answers["msel"] == ['a', 'c']

def test_review_submission_no_edit(monkeypatch):
    form = CLIForm()
    form.answers = {'a': 'x', 'b': 'y'}
    inputs = iter(['n', 'n'])
    monkeypatch.setattr('builtins.input', lambda prompt: next(inputs))
    summary = form.review_submission(allow_edit=True)
    assert summary == {'a': 'x', 'b': 'y'}

def test_review_submission_with_edit(monkeypatch):
    form = CLIForm()
    form.answers = {'a': 'x', 'b': 'y'}
    inputs = iter(['y', 'newx', 'n'])
    monkeypatch.setattr('builtins.input', lambda prompt: next(inputs))
    summary = form.review_submission(allow_edit=True)
    assert summary == {'a': 'newx', 'b': 'y'}

def test_set_renderer_theme():
    form = CLIForm()
    theme = {'color': 'blue', 'border': 'round'}
    form.set_renderer_theme(theme)
    assert form.theme == theme

def test_register_on_change_and_trigger(monkeypatch):
    form = CLIForm()
    calls = []
    def hook(key, value):
        calls.append((key, value))
    form.register_on_change(hook)
    monkeypatch.setattr('builtins.input', lambda prompt: "val")
    form.ask_text("k", "P")
    assert calls == [("k", "val")]

def test_format_errors_list():
    form = CLIForm()
    err = ["e1", "e2"]
    out = form.format_errors(err)
    assert out == "** e1; e2 **"

def test_format_errors_dict_global():
    form = CLIForm()
    errs = {'f': ['e1'], 'g': ['e2', 'e3']}
    out = form.format_errors(errs)
    # order may vary
    assert "f: e1" in out and "g: e2; e3" in out
    assert out.startswith("**") and out.endswith("**")

def test_format_errors_dict_field():
    form = CLIForm()
    errs = {'field': ['bad']}
    out = form.format_errors(errs, field='field')
    assert out == "** bad **"
