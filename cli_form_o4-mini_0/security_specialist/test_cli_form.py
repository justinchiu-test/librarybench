import pytest
import re
import cli_form
import builtins
import getpass

def test_format_errors_default_theme():
    cli_form.set_renderer_theme('default')
    err = cli_form.format_errors('field1', 'error_key', 'Something went wrong')
    assert '[field1:error_key]' in err
    assert 'Something went wrong' in err

def test_set_renderer_theme_dark():
    cli_form.set_renderer_theme('dark')
    assert cli_form.THEME['mode'] == 'dark'
    assert '\033[95m' == cli_form.THEME['colors']['error']

def test_set_renderer_theme_high_contrast():
    cli_form.set_renderer_theme('high-contrast')
    assert cli_form.THEME['mode'] == 'high-contrast'
    assert '\033[93m' == cli_form.THEME['colors']['error']

def test_ask_text_valid(monkeypatch):
    inputs = iter(['test_input'])
    monkeypatch.setattr(builtins, 'input', lambda prompt='': next(inputs))
    value = cli_form.ask_text('Enter text', placeholder='h', length_limit=20, regex=r'\w+', field_name='f1')
    assert value == 'test_input'

def test_ask_text_length_exceeded(monkeypatch):
    inputs = iter(['toolonginput'])
    monkeypatch.setattr(builtins, 'input', lambda prompt='': next(inputs))
    with pytest.raises(cli_form.ValidationError) as exc:
        cli_form.ask_text('Enter', length_limit=5, field_name='f2')
    assert 'length_exceeded' in str(exc.value)

def test_ask_text_invalid_format(monkeypatch):
    inputs = iter(['bad-input'])
    monkeypatch.setattr(builtins, 'input', lambda prompt='': next(inputs))
    with pytest.raises(cli_form.ValidationError) as exc:
        cli_form.ask_text('Enter', regex=r'^\d+$', field_name='f3')
    assert 'invalid_format' in str(exc.value)

def test_branch_flow():
    branches = {'a': [1,2], 'b': [3]}
    assert cli_form.branch_flow('a', branches) == [1,2]
    assert cli_form.branch_flow('c', branches, default=[0]) == [0]

def test_load_choices_async(monkeypatch, tmp_path, capsys):
    call_count = {'count':0}
    def loader():
        call_count['count'] +=1
        return ['x','y']
    # first load
    choices1 = cli_form.load_choices_async(loader, 'key1')
    captured = capsys.readouterr()
    assert 'Loading...' in captured.out
    assert choices1 == ['x','y']
    # second load uses cache
    choices2 = cli_form.load_choices_async(loader, 'key1')
    captured = capsys.readouterr()
    assert 'Loading...' not in captured.out
    assert call_count['count'] == 1

def test_input_line_fallback(monkeypatch):
    monkeypatch.setattr(builtins, 'input', lambda prompt='': 'fallback')
    assert cli_form.input_line_fallback('Prompt') == 'fallback'

def test_review_submission(monkeypatch):
    data = {'a':'1','b':'2'}
    responses = iter(['', 'new2'])
    monkeypatch.setattr(builtins, 'input', lambda prompt='': next(responses))
    result = cli_form.review_submission(data, ['a','b'])
    assert result['a'] == '1'
    assert result['b'] == 'new2'

def test_ask_password(monkeypatch):
    monkeypatch.setattr(getpass, 'getpass', lambda prompt='': 'secretpwd')
    pwd = cli_form.ask_password('Pass', strength_meter=True, field_name='p1')
    assert pwd == 'secretpwd'

def test_select_choices_single(monkeypatch):
    choices = ['one','two']
    monkeypatch.setattr(builtins, 'input', lambda prompt='': '2')
    sel = cli_form.select_choices('Pick', choices, multi=False)
    assert sel == 'two'

def test_select_choices_single_invalid(monkeypatch):
    choices = ['one','two']
    monkeypatch.setattr(builtins, 'input', lambda prompt='': '3')
    with pytest.raises(cli_form.ValidationError):
        cli_form.select_choices('Pick', choices, multi=False)

def test_select_choices_multi(monkeypatch):
    choices = ['a','b','c']
    monkeypatch.setattr(builtins, 'input', lambda prompt='': '1,3')
    sel = cli_form.select_choices('Pick', choices, multi=True)
    assert sel == ['a','c']

def test_register_on_change_and_callback(monkeypatch):
    events = []
    def cb(field, value):
        events.append((field, value))
    cli_form.register_on_change('f', cb)
    monkeypatch.setattr(builtins, 'input', lambda prompt='': 'fire')
    val = cli_form.ask_text('Prompt', field_name='f')
    assert val == 'fire'
    assert events == [('f','fire')]
