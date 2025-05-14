import os
import json
import logging
import pytest
from plugin_api import (
    real_time_validate, apply_skip_logic, WizardNavigator, navigate,
    enable_accessibility_mode, init_curses_renderer, audit_log_event,
    start_wizard, save_session, load_session, register_plugin,
    registry, branch_flow
)

def test_real_time_validate():
    def val(x): return (bool(x), "empty" if not x else "")
    res1 = real_time_validate("test", val)
    assert res1['is_valid']
    assert res1['message'] == ""
    res2 = real_time_validate("", val)
    assert not res2['is_valid']
    assert res2['message'] == "empty"

def test_apply_skip_logic():
    data = {'show': True}
    rule = lambda d: d['show']
    assert apply_skip_logic(rule, data)
    rules = [lambda d: True, lambda d: False]
    assert not apply_skip_logic(rules, data)

def test_navigate():
    pages = ['a', 'b', 'c']
    nav = WizardNavigator(pages)
    assert nav.breadcrumbs == ['a']
    assert navigate('next', nav) == 'b'
    assert navigate('next', nav) == 'c'
    assert navigate('prev', nav) == 'b'
    assert navigate('jump', nav, 0) == 'a'
    assert nav.breadcrumbs == ['a', 'b', 'c', 'b', 'a']
    with pytest.raises(ValueError):
        navigate('invalid', nav)

def test_enable_accessibility_mode():
    cfg = {}
    new_cfg = enable_accessibility_mode(cfg)
    assert new_cfg['aria_label'] == 'widget'
    assert new_cfg['high_contrast']
    assert 'aria_label' not in cfg

def test_init_curses_renderer():
    r = init_curses_renderer()
    assert hasattr(r, 'render_window')
    assert r.render_window() == 'window'

def test_audit_log_event(caplog):
    caplog.set_level(logging.INFO)
    audit_log_event('click', {'id': 1})
    found = False
    for rec in caplog.records:
        if 'click' in rec.getMessage():
            found = True
            break
    assert found

def test_start_wizard():
    wiz = start_wizard(['p1', 'p2'])
    assert wiz.start() == 'p1'
    prog = wiz.progress()
    assert prog['current_index'] == 0
    assert prog['total'] == 2

def test_save_load_session(tmp_path):
    fp = tmp_path / "sess.json"
    save_session('s1', {'a': 1}, str(fp))
    loaded = load_session('s1', str(fp))
    assert loaded == {'a': 1}
    assert load_session('s2', str(fp)) == {}

def test_register_plugin():
    register_plugin('test', validators={'v': lambda x: (True, '')})
    entry = registry.get('test')
    assert 'validators' in entry
    assert 'v' in entry['validators']

def test_branch_flow():
    widgets = [
        {'name': 'w1'},
        {'name': 'w2', 'branch': lambda s: s.get('x') == 1},
        {'name': 'w3', 'branch': lambda s: False}
    ]
    state = {'x': 1}
    res = branch_flow(widgets, state)
    assert [w['name'] for w in res] == ['w1', 'w2']
