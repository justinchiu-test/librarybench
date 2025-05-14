import pytest
import asyncio
from event_system import StateMachine, and_guard, or_guard, not_guard

@pytest.mark.asyncio
async def test_async_guard_allows_transition():
    sm = StateMachine('A')
    async def guard(machine):
        await asyncio.sleep(0)
        return True
    sm.add_transition('go', 'A', 'B', guard=guard)
    result = await sm.trigger('go')
    assert result
    assert sm.current_state == 'B'

@pytest.mark.asyncio
async def test_async_guard_blocks_transition():
    sm = StateMachine('A')
    async def guard(machine):
        await asyncio.sleep(0)
        return False
    sm.add_transition('go', 'A', 'B', guard=guard)
    result = await sm.trigger('go')
    assert not result
    assert sm.current_state == 'A'

@pytest.mark.asyncio
async def test_global_hooks():
    sm = StateMachine('A')
    calls = []
    def before(machine, transition):
        calls.append(('before', transition.name))
    async def after(machine, transition):
        calls.append(('after', transition.name))
    sm.set_global_before_hook(before)
    sm.set_global_after_hook(after)
    sm.add_transition('go', 'A', 'B')
    await sm.trigger('go')
    assert calls == [('before', 'go'), ('after', 'go')]

@pytest.mark.asyncio
async def test_timeout_event():
    sm = StateMachine('A')
    sm.define_timeout_event('A', 'B', timeout=0.01, name='toB')
    await asyncio.sleep(0.02)
    await asyncio.sleep(0)
    assert sm.current_state == 'B'

@pytest.mark.asyncio
async def test_apply_guard():
    sm = StateMachine('A')
    def guard_false(machine):
        return False
    sm.add_transition('go', 'A', 'B')
    sm.apply_guard('go', guard_false)
    result = await sm.trigger('go')
    assert not result
    assert sm.current_state == 'A'

def test_chain_guards():
    def g_true(m): return True
    def g_false(m): return False
    ag = and_guard(g_true, g_true)
    assert asyncio.get_event_loop().run_until_complete(ag(None))
    ag2 = and_guard(g_true, g_false)
    assert not asyncio.get_event_loop().run_until_complete(ag2(None))
    og = or_guard(g_false, g_true)
    assert asyncio.get_event_loop().run_until_complete(og(None))
    og2 = or_guard(g_false, g_false)
    assert not asyncio.get_event_loop().run_until_complete(og2(None))
    ng = not_guard(g_false)
    assert asyncio.get_event_loop().run_until_complete(ng(None))
    ng2 = not_guard(g_true)
    assert not asyncio.get_event_loop().run_until_complete(ng2(None))

@pytest.mark.asyncio
async def test_conditional_exec():
    sm = StateMachine('A')
    calls = []
    def predicate(machine):
        return False
    def callback(machine):
        calls.append('called')
    wrapped = sm.conditional_exec(callback, predicate)
    sm.add_transition('go', 'A', 'B', on_enter=wrapped)
    await sm.trigger('go')
    assert calls == []

@pytest.mark.asyncio
async def test_on_exit_callback():
    sm = StateMachine('A')
    calls = []
    def on_exit(machine):
        calls.append(('exit', machine.current_state))
    sm.add_transition('go', 'A', 'B', on_exit=on_exit)
    await sm.trigger('go')
    assert calls == [('exit', 'A')]
