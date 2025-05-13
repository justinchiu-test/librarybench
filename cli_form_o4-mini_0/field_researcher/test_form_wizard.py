import os
import tempfile
import pytest
from form_wizard import FormWizard

def test_real_time_validate_valid():
    fw = FormWizard()
    assert fw.real_time_validate("25", min=18, max=30) is True
    assert fw.real_time_validate(20, min=10, max=30) is True
    assert fw.real_time_validate("15.5", min=10, max=20) is True

def test_real_time_validate_invalid():
    fw = FormWizard()
    assert fw.real_time_validate("abc", min=0, max=10) is False
    assert fw.real_time_validate(5, min=10, max=20) is False
    assert fw.real_time_validate(25, min=0, max=20) is False

def test_apply_skip_logic_indoor():
    fw = FormWizard()
    q = {'id': 12, 'category': 'Environment'}
    skipped = fw.apply_skip_logic("Indoors", q)
    assert isinstance(skipped, list)
    assert set(skipped) == set(range(10,30))

def test_apply_skip_logic_outdoor():
    fw = FormWizard()
    q = {'id': 12, 'category': 'Environment'}
    skipped = fw.apply_skip_logic("Outdoors", q)
    assert skipped == []
    q2 = {'id': 5, 'category': 'Demographics'}
    assert fw.apply_skip_logic("Indoors", q2) == []

def test_navigation():
    fw = FormWizard()
    first = fw.questions[0]
    assert fw.navigate_next() == fw.questions[1]
    assert fw.current_index == 1
    assert fw.navigate_prev() == first
    assert fw.current_index == 0
    # jump
    q10 = fw.jump_to(10)
    assert q10 == fw.questions[10]
    assert fw.current_index == 10
    # out of bounds jump does nothing
    prev = fw.current_index
    fw.jump_to(100)
    assert fw.current_index == prev

def test_accessibility_mode():
    fw = FormWizard()
    fw.enable_accessibility_mode()
    assert fw.accessibility['high_contrast'] is True
    assert fw.accessibility['screen_reader_cues'] is True

def test_init_curses_renderer():
    fw = FormWizard()
    result = fw.init_curses_renderer()
    assert result is True
    assert fw.curses_initialized is True

def test_audit_log_event():
    fw = FormWizard()
    assert fw.audit_log == []
    fw.audit_log_event("answer", {"q":1, "value":"yes"})
    assert len(fw.audit_log) == 1
    entry = fw.audit_log[0]
    assert entry['event'] == "answer"
    assert 'timestamp' in entry
    assert entry['details'] == {"q":1, "value":"yes"}

def test_start_wizard():
    fw = FormWizard()
    fw.current_index = 5
    fw.history = [0,1,2]
    fw.pages = []
    fw.start_wizard()
    assert fw.current_index == 0
    assert fw.history == []
    assert len(fw.pages) == 3

def test_save_and_load_session(tmp_path):
    fw = FormWizard()
    fw.current_index = 7
    fw.questions[7]['response'] = "test"
    fw.audit_log_event("test", {})
    file = tmp_path / "session.json"
    fw.save_session(str(file))
    # new instance load
    fw2 = FormWizard()
    assert fw2.current_index == 0
    loaded = fw2.load_session(str(file))
    assert loaded is True
    assert fw2.current_index == 7
    assert fw2.questions[7]['response'] == "test"
    assert len(fw2.audit_log) == 1

def test_load_nonexistent_session(tmp_path):
    fw = FormWizard()
    assert fw.load_session(str(tmp_path / "nope.json")) is False

def test_register_plugin():
    fw = FormWizard()
    handler = lambda: "geo"
    fw.register_plugin("geolocation", handler)
    assert "geolocation" in fw.plugins
    assert fw.plugins["geolocation"]() == "geo"

def test_branch_flow():
    fw = FormWizard()
    # default
    pages = fw.branch_flow("Low")
    names = [p['name'] for p in pages]
    assert names == ["Demographics", "Environment", "Feedback"]
    # high risk
    pages2 = fw.branch_flow("High")
    names2 = [p['name'] for p in pages2]
    assert names2 == ["Demographics", "Feedback", "Environment"]
