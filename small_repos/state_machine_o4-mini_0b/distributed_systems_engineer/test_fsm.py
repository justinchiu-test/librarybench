import pytest
import asyncio
from fsm.fsm import FSM

@pytest.mark.asyncio
async def test_simple_transition():
    fsm = FSM('start')
    fsm.add_transition('start', 'go', 'end')
    res = await fsm.trigger('go')
    assert res
    assert fsm.state == 'end'

@pytest.mark.asyncio
async def test_async_callbacks_and_guards():
    fsm = FSM('X')
    async def guard(ctx):
        await asyncio.sleep(0)
        return True
    async def cb(ctx):
        ctx['ok'] = 1
    fsm.add_transition('X', 'e', 'Y', guard=guard, callback=cb)
    await fsm.trigger('e')
    assert fsm.state == 'Y'
    assert fsm.context.get('ok') == 1

@pytest.mark.asyncio
async def test_guard_prevents_transition():
    fsm = FSM('A')
    fsm.add_transition('A', 'go', 'B', guard=lambda ctx: False)
    res = await fsm.trigger('go')
    assert not res
    assert fsm.state == 'A'

@pytest.mark.asyncio
async def test_global_hooks():
    fsm = FSM('s0')
    calls = []
    def before(ctx): calls.append('before')
    async def after(ctx): calls.append('after')
    fsm.register_global_before(before)
    fsm.register_global_after(after)
    fsm.add_transition('s0', 'e', 's1', callback=lambda ctx: calls.append('trans'))
    res = await fsm.trigger('e')
    assert calls == ['before', 'trans', 'after']

@pytest.mark.asyncio
async def test_exit_callback():
    fsm = FSM('X')
    calls = []
    def exit_cb(ctx): calls.append('exit')
    fsm.exit_callback('X', exit_cb)
    fsm.add_transition('X', 'go', 'Y')
    await fsm.trigger('go')
    assert calls == ['exit']

@pytest.mark.asyncio
async def test_compose_guards():
    fsm = FSM('s')
    g1 = lambda ctx: True
    async def g2(ctx): return False
    combined = fsm.compose_guards_logic('AND', g1, g2)
    assert not await combined({})
    combined2 = fsm.compose_guards_logic('OR', g1, g2)
    assert await combined2({})
    notg = fsm.compose_guards_logic('NOT', g1)
    assert not await notg({})

@pytest.mark.asyncio
async def test_conditional_callback():
    fsm = FSM('S')
    calls = []
    def cb(ctx): calls.append('ok')
    wrapped = fsm.conditional_callback('flag', cb)
    fsm.add_transition('S', 'go', 'T', callback=wrapped)
    await fsm.trigger('go')
    assert calls == []
    fsm.state = 'S'
    fsm.context['flag'] = True
    await fsm.trigger('go')
    assert calls == ['ok']
