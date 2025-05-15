import os
import json
import pytest
from game_developer.statemachine import StateMachine

def test_define_and_simulate():
    m = StateMachine()
    m.define_transition("go", "A", "B", "go")
    m.current_state = "A"
    end = m.simulate_sequence(["go"])
    assert end == "B"
    assert m.current_state == "B"

def test_compose_guards_and_or_not():
    def g1(): return True
    def g2(): return False
    and_guard = StateMachine().compose_guards(g1, g2, operator="AND")
    assert not and_guard()
    or_guard = StateMachine().compose_guards(g1, g2, operator="OR")
    assert or_guard()
    not_guard = StateMachine().compose_guards(g2, operator="NOT")
    assert not_guard()

def test_on_enter_and_hooks(tmp_path):
    m = StateMachine()
    log = []
    def on_enter_cb(machine, ev, t): log.append(("enter", machine.current_state))
    def before_cb(machine, ev, t): log.append(("before", ev))
    def after_cb(machine, ev, t): log.append(("after", ev))
    m.on_enter("B", on_enter_cb)
    m.add_global_hook("before", before_cb)
    m.add_global_hook("after", after_cb)
    m.define_transition("go", "A", "B", "go")
    m.current_state = "A"
    m.simulate_sequence(["go"])
    assert log == [("before", "go"), ("enter", "B"), ("after", "go")]

def test_serialize_and_load():
    m = StateMachine()
    m.define_transition("t1", "X", "Y", "go")
    m.current_state = "X"
    d = m.export_machine(format="dict")
    assert isinstance(d, dict)
    j = m.export_machine(format="json")
    loaded = StateMachine.load_machine(j)
    assert loaded.states == m.states
    assert loaded.transitions == m.transitions
    assert loaded.current_state == m.current_state

def test_undo_redo():
    m = StateMachine()
    m.define_transition("go", "A", "B", "go")
    m.current_state = "A"
    m.simulate_sequence(["go"])
    assert m.current_state == "B"
    ev = m.pop_undo()
    assert ev['trigger'] == "go"
    assert m.current_state == "A"
    # pop again returns next redo
    ev2 = m.pop_undo()
    assert ev2 is None

def test_export_visualization(tmp_path):
    file = tmp_path / "graph.dot"
    m = StateMachine()
    m.define_transition("go", "A", "B", "go")
    m.define_transition("back", "B", "A", "back")
    path = m.export_visualization(str(file))
    assert os.path.exists(path)
    content = file.read_text()
    assert '"A" -> "B"' in content
    assert '"B" -> "A"' in content

def test_enable_history():
    m = StateMachine()
    m.enable_history("S", mode="shallow")
    assert m.history_enabled["S"] == "shallow"
