import os
import pickle
import pytest
from wizard.form_engine import FormEngine

def test_start_wizard_and_history_and_logs():
    engine = FormEngine()
    flow = [{'name': 'page1'}, {'name': 'page2'}]
    first = engine.start_wizard(flow)
    assert first == flow[0]
    assert engine.current_page_index == 0
    assert engine.history == [0]
    # check log
    assert any("Wizard started" in e for _, e in engine.logs)

def test_navigate_next_prev_and_jump():
    engine = FormEngine()
    flow = ['p0', 'p1', 'p2']
    engine.start_wizard(flow)
    assert engine.navigate('next') == 'p1'
    assert engine.current_page_index == 1
    assert engine.history[-1] == 1
    assert engine.navigate('prev') == 'p0'
    assert engine.current_page_index == 0
    page2 = engine.navigate(2)
    assert page2 == 'p2'
    assert engine.current_page_index == 2
    # out of bounds
    with pytest.raises(IndexError):
        engine.navigate('next')
    with pytest.raises(IndexError):
        engine.navigate(-1)
    with pytest.raises(ValueError):
        engine.navigate('invalid')

def test_real_time_validate_default_and_custom():
    engine = FormEngine()
    # default validator: empty string invalid
    valid, msg = engine.real_time_validate('field', '')
    assert not valid
    assert "cannot be empty" in msg
    assert any("failed" in e for _, e in engine.logs)
    # custom validator
    def is_number(val):
        if isinstance(val, int):
            return True, ""
        return False, "Not a number"
    engine.add_validator('age', is_number)
    ok, m2 = engine.real_time_validate('age', 30)
    assert ok and m2 == ""
    bad, m3 = engine.real_time_validate('age', 'abc')
    assert not bad and m3 == "Not a number"

def test_apply_skip_logic():
    engine = FormEngine()
    # skip 'b' if a == 'skip'
    engine.add_skip_condition('b', lambda data: data.get('a') == 'skip')
    data1 = {'a': 'skip', 'b': 'should_skip', 'c': 'ok'}
    result1 = engine.apply_skip_logic(data1)
    assert 'b' not in result1
    assert 'a' in result1 and 'c' in result1
    # no skip
    data2 = {'a': 'keep', 'b': 'value'}
    result2 = engine.apply_skip_logic(data2)
    assert result2 == data2

def test_accessibility_mode_and_renderer():
    engine = FormEngine()
    res = engine.enable_accessibility_mode()
    assert res['accessibility_mode'] and res['high_contrast']
    assert engine.accessibility_mode and engine.high_contrast
    assert any("Accessibility mode enabled" in e for _, e in engine.logs)
    rc = engine.init_curses_renderer()
    assert rc
    assert engine.renderer_initialized
    assert any("Curses renderer initialized" in e for _, e in engine.logs)

def test_audit_log_event_manual():
    engine = FormEngine()
    before = len(engine.logs)
    engine.audit_log_event("Test event")
    assert len(engine.logs) == before + 1
    assert engine.logs[-1][1] == "Test event"

def test_save_and_load_session(tmp_path):
    engine = FormEngine()
    engine.enable_accessibility_mode()
    engine.start_wizard([{'n':1}])
    fname = tmp_path / "sess.pkl"
    engine.save_session(str(fname))
    assert os.path.exists(str(fname))
    loaded = FormEngine.load_session(str(fname))
    # loaded is a FormEngine
    assert isinstance(loaded, FormEngine)
    # state preserved
    assert loaded.accessibility_mode
    assert loaded.flow == [{'n':1}]
    # log contains load event
    assert any("Session loaded" in e for _, e in loaded.logs)

def test_register_plugin_and_duplicate():
    engine = FormEngine()
    def plugin(): pass
    engine.register_plugin('p1', plugin)
    assert 'p1' in engine.plugins and engine.plugins['p1'] is plugin
    with pytest.raises(ValueError):
        engine.register_plugin('p1', plugin)

def test_branch_flow():
    engine = FormEngine()
    pages = [
        {'name':'common'},
        {'name':'simple1','detail_level':'simple'},
        {'name':'detailed1','detail_level':'detailed'},
    ]
    engine.start_wizard(pages)
    simple = engine.branch_flow('simple')
    assert len(simple) == 2
    assert all(p['name'] in ('common','simple1') for p in simple)
    detailed = engine.start_wizard(pages) or engine.branch_flow('detailed')
    assert len(engine.flow) == 2
    assert all(p['name'] in ('common','detailed1') for p in engine.flow)
    with pytest.raises(ValueError):
        engine.branch_flow('invalid')
