import pytest
from form_engine import FormEngine

def test_ask_text_length_valid():
    engine = FormEngine()
    result = engine.ask_text("Alice", min_len=2, max_len=10)
    assert result == "Alice"

def test_ask_text_length_invalid():
    engine = FormEngine()
    with pytest.raises(ValueError) as e:
        engine.ask_text("A", min_len=2, max_len=5)
    assert "between 2 and 5" in str(e.value)

def test_ask_text_pattern_valid():
    engine = FormEngine()
    email = "test@example.com"
    result = engine.ask_text(email, pattern=r"[^@]+@[^@]+\.[^@]+")
    assert result == email

def test_ask_text_pattern_invalid():
    engine = FormEngine()
    with pytest.raises(ValueError):
        engine.ask_text("invalid_email", pattern=r"[^@]+@[^@]+\.[^@]+")

def test_branch_flow_engineering():
    engine = FormEngine()
    flow = engine.branch_flow("engineering")
    assert flow == ['coding_skills', 'system_design', 'behavioral']

def test_branch_flow_marketing():
    engine = FormEngine()
    flow = engine.branch_flow("marketing")
    assert flow == ['market_analysis', 'creativity', 'behavioral']

def test_branch_flow_unknown():
    engine = FormEngine()
    flow = engine.branch_flow("other")
    assert flow == ['general']

def test_load_choices_async_caching():
    engine = FormEngine()
    calls = {'count': 0}
    def fetch():
        calls['count'] += 1
        return ['a', 'b']
    first = engine.load_choices_async('jobs', fetch)
    second = engine.load_choices_async('jobs', fetch)
    assert first == ['a', 'b']
    assert second == ['a', 'b']
    assert calls['count'] == 1

def test_input_line_fallback():
    engine = FormEngine()
    assert engine.input_line_fallback("Prompt:", "response") == "response"

def test_review_submission_no_edit():
    engine = FormEngine()
    entries = {'name': 'Alice', 'score': 5}
    summary = engine.review_submission(entries.copy())
    assert "name: Alice" in summary
    assert "score: 5" in summary

def test_review_submission_with_edit():
    engine = FormEngine()
    entries = {'name': 'Alice', 'score': 5}
    summary = engine.review_submission(entries, edit_key='score', new_value=4)
    assert "score: 4" in summary

def test_ask_password_hide_and_strength():
    engine = FormEngine()
    masked = engine.ask_password("Passw0rd", show=False)
    assert masked == "********"
    assert engine.last_strength == 'strong'

def test_ask_password_show_and_strength():
    engine = FormEngine()
    pwd = "short"
    shown = engine.ask_password(pwd, show=True)
    assert shown == pwd
    assert engine.last_strength == 'weak'

def test_select_choices_single():
    engine = FormEngine()
    choices = ['a', 'b', 'c']
    assert engine.select_choices(choices, 1) == 'b'
    assert engine.select_choices(choices, [2]) == 'c'

def test_select_choices_multiple():
    engine = FormEngine()
    choices = ['a', 'b', 'c', 'd']
    result = engine.select_choices(choices, [1,3], multiple=True)
    assert result == ['b', 'd']

def test_set_renderer_theme():
    engine = FormEngine()
    palette = {'fg': 'white', 'bg': 'blue'}
    engine.set_renderer_theme('default', palette)
    assert engine.themes['default'] == palette

def test_register_and_trigger_on_change():
    engine = FormEngine()
    calls = []
    def hook(field, value):
        calls.append((field, value))
    engine.register_on_change('rating', hook)
    engine.trigger_on_change('rating', 5)
    assert calls == [('rating', 5)]

def test_format_errors():
    engine = FormEngine()
    errors = [('name', 'required'), ('score', 'invalid')]
    out = engine.format_errors(errors)
    lines = out.split('\n')
    assert "[name] required" in lines
    assert "[score] invalid" in lines
