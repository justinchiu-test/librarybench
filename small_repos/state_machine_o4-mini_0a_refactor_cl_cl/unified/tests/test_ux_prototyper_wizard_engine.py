import pytest
from src.interfaces.ux_prototyper.wizard_engine import WizardEngine, compose_guards

def test_define_transition_and_states():
    w = WizardEngine()
    w.define_transition('t1', 'A', 'B', 'go')
    assert {'name':'t1','from':'A','to':'B','trigger':'go','guard':None} in w.transitions
    assert 'A' in w.states and 'B' in w.states

def test_compose_guards_and_or():
    def true(): return True
    def false(): return False
    guard_and = compose_guards(true, false, operator='AND')
    assert guard_and() == False
    guard_or = compose_guards(true, false, operator='OR')
    assert guard_or() == True
    with pytest.raises(ValueError):
        compose_guards(true, false, operator='XOR')

def test_on_enter_hook_called():
    w = WizardEngine()
    called = []
    def hook(): called.append('x')
    w.on_enter('B', hook)
    w.current_state = 'A'
    w.define_transition('t1', 'A', 'B', 'go')
    w.trigger('go')
    assert called == ['x']

def test_global_hooks():
    w = WizardEngine()
    calls = []
    def before(trigger, from_s, to_s): calls.append(('b', trigger, from_s, to_s))
    def after(trigger, from_s, to_s): calls.append(('a', trigger, from_s, to_s))
    w.add_global_hook('before', before)
    w.add_global_hook('after', after)
    w.current_state = 'A'
    w.define_transition('t1', 'A', 'B', 'go')
    w.trigger('go')
    assert calls[0][0] == 'b' and calls[1][0] == 'a'

def test_export_and_load_machine():
    w = WizardEngine()
    w.define_transition('t1', 'A', 'B', 'go')
    w.define_transition('t2', 'B', 'C', 'next')
    w.on_enter('C', lambda: None)
    w.add_global_hook('after', lambda *args: None)
    w.enable_history('grp', mode='deep')
    data = w.export_machine()
    w2 = WizardEngine()
    w2.load_machine(data)
    data2 = w2.export_machine()
    assert data['states'] == data2['states']
    assert len(data['transitions']) == len(data2['transitions'])
    assert data['history_settings'] == data2['history_settings']

def test_undo_redo():
    w = WizardEngine()
    w.current_state = 'A'
    w.define_transition('t1', 'A', 'B', 'go')
    new = w.push_undo('go')
    assert new == 'B'
    old = w.pop_undo()
    assert old == 'A'

def test_export_visualization():
    w = WizardEngine()
    w.define_transition('t1', 'A', 'B', 'go')
    vis = w.export_visualization()
    assert 'nodes' in vis and 'edges' in vis
    assert ('A','B','go') in vis['edges']

def test_simulate_sequence():
    w = WizardEngine()
    w.define_transition('t1', 'A', 'B', 'go')
    w.define_transition('t2', 'B', 'C', 'next')
    w.current_state = 'A'
    result = w.simulate_sequence(['go','next'], expect_states=['B','C'])
    assert result == ['B','C']

def test_enable_history():
    w = WizardEngine()
    w.enable_history('grp', mode='full')
    assert w.history_settings['grp'] == 'full'

def test_run_tests():
    w = WizardEngine()
    assert w.run_tests() == True