import os
import json
import pytest
from form_engine import CLIFormEngine

def test_real_time_validate_ip_valid():
    engine = CLIFormEngine()
    assert engine.real_time_validate('ip', '192.168.0.1') is True
    last = engine.audit_log[-1]
    assert last['event'] == 'validation_success'

def test_real_time_validate_ip_invalid():
    engine = CLIFormEngine()
    assert engine.real_time_validate('ip', '999.999.999.999') is False
    last = engine.audit_log[-1]
    assert last['event'] == 'validation_failure'

def test_real_time_validate_hostname_valid():
    engine = CLIFormEngine()
    assert engine.real_time_validate('hostname', 'host-01') is True
    last = engine.audit_log[-1]
    assert last['event'] == 'validation_success'

def test_real_time_validate_hostname_invalid():
    engine = CLIFormEngine()
    assert engine.real_time_validate('hostname', 'host name') is False
    last = engine.audit_log[-1]
    assert last['event'] == 'validation_failure'

def test_apply_skip_logic_on():
    engine = CLIFormEngine()
    engine.session_data['stateless_mode'] = True
    engine.apply_skip_logic()
    assert 'Storage' not in engine.steps
    assert engine.skip_mode is True
    assert any(e['event']=='skip_logic_applied' for e in engine.audit_log)

def test_apply_skip_logic_off():
    engine = CLIFormEngine()
    engine.session_data['stateless_mode'] = False
    engine.apply_skip_logic()
    assert engine.steps == engine.default_steps
    assert engine.skip_mode is False
    assert any(e['event']=='skip_logic_reset' for e in engine.audit_log)

def test_navigation_next_prev_jump_and_bounds():
    engine = CLIFormEngine()
    engine.start_wizard()
    assert engine.current_step() == 'Network'
    # next
    assert engine.navigate('next') == 'Storage'
    # prev
    assert engine.navigate('prev') == 'Network'
    # jump by name
    assert engine.navigate('jump', 'Review') == 'Review'
    # jump by index
    assert engine.navigate('jump', 1) == 'Storage'
    # bounds
    with pytest.raises(IndexError):
        engine.navigate('prev')
    engine.current_idx = len(engine.steps)-1
    with pytest.raises(IndexError):
        engine.navigate('next')
    with pytest.raises(ValueError):
        engine.navigate('jump', 'NonExistent')
    with pytest.raises(IndexError):
        engine.navigate('jump', 999)

def test_enable_accessibility_mode():
    engine = CLIFormEngine()
    assert engine.accessibility is False
    engine.enable_accessibility_mode()
    assert engine.accessibility is True
    assert any(e['event']=='accessibility_enabled' for e in engine.audit_log)

def test_init_curses_renderer():
    engine = CLIFormEngine()
    res = engine.init_curses_renderer()
    assert res == 'initialized'
    assert engine.curses_renderer == 'initialized'
    assert any(e['event']=='curses_initialized' for e in engine.audit_log)

def test_audit_log_event_timestamp_and_content():
    engine = CLIFormEngine()
    engine.audit_log_event('test_event', {'key':'value'})
    entry = engine.audit_log[-1]
    assert entry['event'] == 'test_event'
    assert entry['details'] == {'key':'value'}
    assert entry['timestamp'].endswith('Z')

def test_start_wizard_resets_state():
    engine = CLIFormEngine()
    engine.current_idx = 2
    engine.history = [{'from':0,'to':2,'action':'next'}]
    engine.audit_log = []
    step = engine.start_wizard()
    assert step == 'Network'
    assert engine.current_idx == 0
    assert engine.history == []
    assert any(e['event']=='wizard_started' for e in engine.audit_log)

def test_save_and_load_session(tmp_path):
    engine = CLIFormEngine()
    engine.session_data = {'stateless_mode': True}
    engine.apply_skip_logic()
    engine.current_idx = 1
    engine.accessibility = True
    file_path = tmp_path / "sess.json"
    engine.save_session(str(file_path))
    assert file_path.exists()
    data = json.loads(file_path.read_text())
    assert data['skip_mode'] is True
    # load into new engine
    e2 = CLIFormEngine()
    step = e2.load_session(str(file_path))
    assert step == e2.current_step()
    assert e2.skip_mode is True
    assert any(e['event']=='session_loaded' for e in e2.audit_log)

def test_register_plugin_and_duplicate():
    engine = CLIFormEngine()
    def dummy(): pass
    engine.register_plugin('vm_selector', dummy)
    assert 'vm_selector' in engine.plugins
    with pytest.raises(ValueError):
        engine.register_plugin('vm_selector', dummy)
    assert any(e['event']=='plugin_registered' for e in engine.audit_log)

def test_branch_flow_quick_deploy_and_special():
    engine = CLIFormEngine()
    seq = engine.branch_flow(quick_deploy=True)
    assert seq[1] == 'Services' and seq[2] == 'Storage'
    seq2 = engine.branch_flow(external_status='special')
    assert seq2[-1] == 'Network'
    assert any(e['event']=='flow_branced' for e in engine.audit_log)
