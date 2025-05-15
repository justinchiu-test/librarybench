import pytest
from business_process_analyst.process_engine import (
    reset_machine,
    define_transition,
    compose_guards,
    on_enter,
    add_global_hook,
    export_machine,
    load_machine,
    push_undo,
    pop_undo,
    export_visualization,
    simulate_sequence,
    enable_history,
    run_tests,
    _default_machine
)

@pytest.fixture(autouse=True)
def reset():
    reset_machine()

def test_compose_guards_and_or():
    true = lambda: True
    false = lambda: False
    and_guard = compose_guards(true, false, operator='AND')
    or_guard = compose_guards(true, false, operator='OR')
    assert and_guard() is False
    assert or_guard() is True

def test_define_transition_and_on_enter_and_global_hook():
    events = []
    def manager_approval(): return True
    def invoice_callback(): events.append('invoiced')
    def audit_hook(info): events.append(f"audit:{info['name']}")
    define_transition("approve_order", "pending", "approved", manager_approval)
    define_transition("invoiced", "approved", "invoiced", None)
    on_enter("invoiced", invoice_callback)
    add_global_hook("after", audit_hook)
    simulate_sequence(["approve_order", "invoiced"], assert_final="invoiced")
    assert "invoiced" in events
    assert "audit:approve_order" in events
    assert "audit:invoiced" in events

def test_undo_redo():
    define_transition("approve", "pending", "approved")
    push_undo("approve")
    simulate_sequence(["approve"], assert_final="approved")
    evt = pop_undo()
    assert evt == "approve"
    # state reverted to pending
    assert _default_machine.current_state == "pending"

def test_export_and_load_machine():
    define_transition("t1","s1","s2")
    y = export_machine("yaml")
    assert isinstance(y, str)
    load_machine(y)
    y2 = export_machine("yaml")
    assert y2 == y

def test_export_visualization():
    define_transition("t1","s1","s2")
    dot = export_visualization("dot")
    assert dot.startswith("digraph")

def test_enable_history_and_run_tests():
    enable_history("order_group", mode="deep")
    assert _default_machine.history_modes.get("order_group") == "deep"
    assert run_tests() is True
