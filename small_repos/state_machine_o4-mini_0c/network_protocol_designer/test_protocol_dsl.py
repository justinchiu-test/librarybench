import json
import pytest
from protocol_dsl import (
    define_transition, compose_guards, on_enter, add_global_hook,
    export_machine, load_machine, push_undo, pop_redo,
    export_visualization, simulate_sequence, enable_history
)

# Dummy functions for testing
def check_checksum(pkt): pass
def validate_seq(pkt): pass
def on_receive_synack(pkt): pass
def start_keepalive_timer(): pass
def drop_if_invalid(pkt): pass

def test_define_and_simulate_transition():
    # Reset machine
    load_machine(json.dumps({'states': [], 'transitions': [], 'guards': [], 'on_enter': {}, 'global_hooks': {}, 'history': {}}))
    define_transition("SYN→ACK", "SYN_SENT", "ESTABLISHED", on_receive_synack)
    result = simulate_sequence(["SYN→ACK"], expected="ESTABLISHED")
    assert result is True

def test_compose_guards():
    comp = compose_guards(check_checksum, validate_seq, operator="AND")
    assert comp['guards'] == ['check_checksum', 'validate_seq']
    assert comp['operator'] == 'AND'

def test_on_enter_and_global_hook_and_history():
    on_enter("ESTABLISHED", start_keepalive_timer)
    add_global_hook("before", drop_if_invalid)
    enable_history("session", mode="shallow")
    spec = json.loads(export_machine("json"))
    assert "ESTABLISHED" in spec['on_enter']
    assert 'start_keepalive_timer' in spec['on_enter']['ESTABLISHED']
    assert 'drop_if_invalid' in spec['global_hooks']['before']
    assert spec['history']['session'] == 'shallow'

def test_undo_redo():
    push_undo("evt1")
    push_undo("evt2")
    evt = pop_redo()
    assert evt == "evt2"
    evt2 = pop_redo()
    assert evt2 == "evt1"
    evt_none = pop_redo()
    assert evt_none is None

def test_export_and_load_machine():
    # Setup
    load_machine(json.dumps({'states': [], 'transitions': [], 'guards': [], 'on_enter': {}, 'global_hooks': {}, 'history': {}}))
    define_transition("A→B", "A", "B", on_receive_synack)
    compose_guards(check_checksum, validate_seq)
    on_enter("B", start_keepalive_timer)
    spec_json = export_machine("json")
    # Reload
    load_machine(spec_json)
    spec = json.loads(export_machine("json"))
    assert any(t['name'] == "A→B" for t in spec['transitions'])
    assert spec['guards'], "Guards should not be empty"

def test_export_visualization():
    load_machine(json.dumps({'states': [], 'transitions': [], 'guards': [], 'on_enter': {}, 'global_hooks': {}, 'history': {}}))
    define_transition("X→Y", "X", "Y", on_receive_synack)
    dot = export_visualization("graphviz")
    assert 'digraph G' in dot
    assert '"X" -> "Y" [label="X→Y"]' in dot

def test_simulate_sequence_fail():
    load_machine(json.dumps({'states': [], 'transitions': [], 'guards': [], 'on_enter': {}, 'global_hooks': {}, 'history': {}}))
    define_transition("A→B", "A", "B", on_receive_synack)
    # Wrong start state
    result = simulate_sequence(["A→B"], expected="B")
    assert result is True
    # Nonexistent transition
    fail = simulate_sequence(["NON"], expected="B")
    assert fail is False
