import pytest
import src.interfaces.robotics_engineer.yaml as yaml
from src.interfaces.robotics_engineer.robotfsm import (
    reset_machine, define_transition, compose_guards, on_enter,
    add_global_hook, export_machine, load_machine, push_undo,
    pop_redo, export_visualization, simulate_sequence,
    enable_history, get_undo_stack, get_redo_stack,
    get_history_modes, set_initial, STATE_MACHINE
)

def test_define_transition_and_states():
    reset_machine()
    define_transition('t1', 'a', 'b', 'e1')
    define_transition('t2', 'b', 'c', 'e2')
    # simulate sequence
    set_initial('a')
    end = simulate_sequence(['e1', 'e2'])
    assert end == 'c'
    assert 'a' in export_machine()

def test_compose_guards_and_or():
    ga = lambda x: x > 5
    gb = lambda x: x < 10
    gand = compose_guards(ga, gb, "AND")
    gor = compose_guards(ga, gb, "OR")
    assert gand(7) is True
    assert gand(4) is False
    assert gor(12) is True

    with pytest.raises(ValueError):
        compose_guards(ga, gb, "XOR")

def test_on_enter_and_global_hooks():
    reset_machine()
    calls = []
    def before_hook(ev, src, dst):
        calls.append('before')
    def enter_hook(ev, state):
        calls.append('enter')
    add_global_hook('before', before_hook)
    define_transition('t1', 'start', 'mid', 'go')
    on_enter('mid', enter_hook)
    set_initial('start')
    simulate_sequence(['go'])
    assert calls == ['before', 'enter']

def test_export_and_load_machine():
    reset_machine()
    define_transition('t1', 'x', 'y', 'ev1')
    define_transition('t2', 'y', 'z', 'ev2')
    yaml_str = export_machine()
    data = yaml.safe_load(yaml_str)
    assert set(data['states']) == {'x', 'y', 'z'}
    reset_machine()
    load_machine(yaml_str)
    assert len(STATE_MACHINE.transitions) == 2
    # Round-trip consistency
    yaml2 = export_machine()
    assert yaml.safe_load(yaml2) == data

def test_undo_redo_stacks():
    reset_machine()
    assert get_undo_stack() == []
    push_undo('e1')
    assert get_undo_stack() == ['e1']
    assert pop_redo() is None
    # manually add redo
    get_redo_stack().append('r1')
    assert pop_redo() == 'r1'

def test_export_visualization():
    reset_machine()
    define_transition('t1', 's1', 's2', 'ev')
    dot = export_visualization()
    assert 's1' in dot and 's2' in dot and 'ev' in dot
    with pytest.raises(ValueError):
        export_visualization(format="png")

def test_enable_history():
    reset_machine()
    hm = enable_history('transport', mode="shallow")
    assert hm['transport'] == 'shallow'
    modes = get_history_modes()
    assert 'transport' in modes

def test_simulate_sequence_assertion():
    reset_machine()
    define_transition('t1', None, 'only', 'e1')
    # sequence leads to 'only'
    end = simulate_sequence(['e1'])
    assert end == 'only'
    # bad sequence raises
    with pytest.raises(Exception):
        simulate_sequence(['bad'])