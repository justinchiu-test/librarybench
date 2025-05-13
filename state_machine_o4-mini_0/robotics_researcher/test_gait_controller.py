import pytest
import asyncio
from gait_controller import GaitController, SimulationHarness

def test_global_hooks_invoked():
    gait = GaitController()
    log = []
    def before(f, t): log.append(f"before {f}->{t}")
    def after(f, t): log.append(f"after {f}->{t}")
    gait.add_global_before(before)
    gait.add_global_after(after)
    gait.current_state = "idle"
    gait.register_transition("go", "walk")
    ok = gait.transition("go")
    assert ok
    assert gait.current_state == "walk"
    assert log == ["before idle->walk", "after idle->walk"]

def test_on_exit_gait_hook():
    gait = GaitController()
    called = []
    def exit_hook(state): called.append(state)
    gait.add_on_exit_gait(exit_hook)
    gait.current_state = "walk"
    gait.register_transition("exit_gait", "idle")
    ok = gait.transition("exit_gait")
    assert ok
    assert called == ["idle"]

def test_guard_blocks_transition():
    gait = GaitController()
    gait.current_state = "idle"
    gait.register_transition("go", "walk", guard=lambda: False)
    ok = gait.transition("go")
    assert not ok
    assert gait.current_state == "idle"

def test_guard_allows_transition():
    gait = GaitController()
    gait.current_state = "idle"
    gait.register_transition("go", "walk", guard=lambda: True)
    ok = gait.transition("go")
    assert ok
    assert gait.current_state == "walk"

def test_guard_composition_and_or():
    p_true = lambda: True
    p_false = lambda: False
    and_pred = GaitController.guard_and(p_true, p_false)
    or_pred = GaitController.guard_or(p_false, p_true)
    assert not and_pred()
    assert or_pred()

def test_conditional_on_decorator():
    executed = []
    def cond(): return True
    @GaitController.conditional_on(cond)
    def risky():
        executed.append(True)
    risky()
    assert executed == [True]
    executed.clear()
    def cond2(): return False
    @GaitController.conditional_on(cond2)
    def risky2():
        executed.append(True)
    risky2()
    assert executed == []

@pytest.mark.asyncio
async def test_async_transition_and_timeout():
    gait = GaitController()
    gait.current_state = "idle"
    gait.register_transition("start", "walk", timeout=0.1)
    gait.register_transition("stop_gait", "idle")
    gait.set_foot_contact(False)
    result = await gait.transition_async("start")
    assert result
    # wait longer than timeout
    await asyncio.sleep(0.2)
    assert gait.current_state == "idle"

def test_simulation_harness():
    gait = GaitController()
    sim = gait.create_simulation_harness()
    seq = ["lift", "place", "push"]
    sim.drive(seq)
    assert sim.stub_motor_commands == seq
    assert sim.assert_stability()
