import asyncio
import pytest
from statemachine.statemachine import StateMachine, TransitionError

@pytest.mark.anyio
async def test_basic_transition_and_hooks():
    sm = StateMachine('off')
    order = []
    async def before(m, name):
        order.append(f"before {name}")
    async def after(m, name):
        order.append(f"after {name}")
    sm.add_global_before_hook(before)
    sm.add_global_after_hook(after)
    sm.add_transition('turn_on', 'off', 'on')
    old, new = await sm.async_transition('turn_on')
    assert (old, new) == ('off', 'on')
    assert sm.state == 'on'
    assert order == ['before turn_on', 'after turn_on']

@pytest.mark.anyio
async def test_guard_blocks_transition():
    sm = StateMachine('s1')
    def guard():
        return False
    sm.add_transition('t', 's1', 's2', guard=guard)
    with pytest.raises(TransitionError):
        await sm.async_transition('t')

@pytest.mark.anyio
async def test_async_guard_and_action():
    sm = StateMachine('A')
    async def guard(x):
        await asyncio.sleep(0.01)
        return x > 0
    async def action(x):
        await asyncio.sleep(0.01)
        sm.note = x
    sm.add_transition('go', 'A', 'B', guard=guard, action=action)
    await sm.async_transition('go', 5)
    assert sm.state == 'B'
    assert sm.note == 5

def test_compose_guards():
    def g1(x): return x > 0
    def g2(x): return x % 2 == 0
    andg = StateMachine.compose_guards_and(g1, g2)
    org = StateMachine.compose_guards_or(g1, g2)
    notg = StateMachine.compose_guard_not(g1)
    assert andg(4)
    assert not andg(3)
    assert org(3)
    assert not org(-1)
    assert notg(1)
    assert not notg(0)

@pytest.mark.anyio
async def test_conditional_callback():
    sm = StateMachine('idle')
    calls = []
    def pred(temp):
        return temp > 100
    async def notify(temp):
        calls.append(temp)
    cc = StateMachine.conditional_callback(pred, notify)
    await cc(50)
    await cc(150)
    assert calls == [150]

@pytest.mark.anyio
async def test_on_exit_state():
    sm = StateMachine('X')
    calls = []
    def cb(state, name):
        calls.append((state, name))
    StateMachine.on_exit_state('X', cb)(sm)
    sm.add_transition('toY', 'X', 'Y')
    await sm.async_transition('toY')
    assert calls == [('X', 'toY')]

@pytest.mark.anyio
async def test_timeout_transition():
    sm = StateMachine('s1')
    sm.add_transition('auto', 's1', 's2')
    sm.define_timeout('auto', 0.05)
    await asyncio.sleep(0.1)
    assert sm.state == 's2'

@pytest.mark.anyio
async def test_simulate_sequence_and_regions():
    sm1 = StateMachine('off')
    sm1.add_transition('on', 'off', 'on')
    sm2 = StateMachine('cold')
    sm2.add_transition('heat', 'cold', 'hot')
    sm = StateMachine('root')
    sm.add_region('light', sm1)
    sm.add_region('thermo', sm2)
    final = await StateMachine.simulate_sequence(sm1, ['on'])
    assert final == 'on'
    final2 = await StateMachine.simulate_sequence(sm2, ['heat'])
    assert final2 == 'hot'
    assert sm._regions['light'] is sm1
    assert sm._regions['thermo'] is sm2

def test_scaffold_cli():
    text = StateMachine.scaffold_cli('house')
    assert "CLI scaffold for house" in text
