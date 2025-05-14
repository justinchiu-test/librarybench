import asyncio
import pytest
import sys
import json
from ai_state_machine import StateMachine
from utils import (
    guard_function,
    compose_guard_set_and,
    compose_guard_set_or,
    compose_guard_set_not,
    run_if,
    simulate_and_assert
)
import cli

@pytest.fixture(autouse=True)
def event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    return loop

def test_basic_transition(event_loop):
    sm = StateMachine('idle', loop=event_loop)
    sm.add_state('idle')
    sm.add_state('patrol')
    sm.add_transition('idle', 'start_patrol', 'patrol')
    event_loop.run_until_complete(sm.handle_event('start_patrol'))
    assert sm.current_state == 'patrol'

@pytest.mark.asyncio
async def test_async_guard_and_action(event_loop):
    sm = StateMachine('idle', loop=event_loop)
    sm.add_state('idle')
    sm.add_state('running')
    async def guard(c):
        return True
    async def action(c):
        c['runned'] = True
    sm.add_transition('idle', 'go', 'running', guard=guard, action=action)
    context = {}
    await sm.handle_event('go', context)
    assert sm.current_state == 'running'
    assert context.get('runned')

def test_global_hooks(event_loop):
    sm = StateMachine('s1', loop=event_loop)
    sm.add_state('s1')
    sm.add_state('s2')
    order = []
    def before(s,t,e,c):
        order.append(('before', s, t))
    def after(s,t,e,c):
        order.append(('after', s, t))
    sm.before_transition_global(before)
    sm.after_transition_global(after)
    sm.add_transition('s1', 'e', 's2')
    event_loop.run_until_complete(sm.handle_event('e'))
    assert order == [('before','s1','s2'),('after','s1','s2')]

def test_timeout_transition(event_loop):
    sm = StateMachine('idle', loop=event_loop)
    sm.add_state('idle')
    sm.add_state('searching')
    sm.add_timeout_transition('idle', 0.05, 'timeout', 'searching')
    # enter idle to schedule
    event_loop.run_until_complete(sm.states['idle']['on_enter']())
    # wait to trigger timeout
    event_loop.run_until_complete(asyncio.sleep(0.1))
    assert sm.current_state == 'searching'

def test_guards():
    def g1(c): return True
    def g2(c): return False
    andg = compose_guard_set_and(guard_function(g1), guard_function(g2))
    res = asyncio.get_event_loop().run_until_complete(andg({}))
    assert not res
    org = compose_guard_set_or(guard_function(g1), guard_function(g2))
    res2 = asyncio.get_event_loop().run_until_complete(org({}))
    assert res2
    notg = compose_guard_set_not(guard_function(g2))
    res3 = asyncio.get_event_loop().run_until_complete(notg({}))
    assert res3

def test_run_if():
    called = {'x':False}
    def pred(c): return c.get('ok')
    def fn(c): c['x'] = True
    runner = run_if(pred, fn)
    ctx = {'ok': True}
    asyncio.get_event_loop().run_until_complete(runner(ctx))
    assert ctx['x']

def test_simulate_and_assert(event_loop):
    sm = StateMachine('a', loop=event_loop)
    sm.add_state('a')
    sm.add_state('b')
    sm.add_state('c')
    sm.add_transition('a','to_b','b')
    sm.add_transition('b','to_c','c')
    simulate_and_assert(sm,['to_b','to_c'],'c')

def test_on_exit(event_loop):
    sm = StateMachine('pursuit', loop=event_loop)
    sm.add_state('pursuit', on_enter=None, on_exit=lambda c: c.update({'reset':True}))
    sm.add_state('idle')
    sm.add_transition('pursuit','lose','idle')
    ctx = {}
    event_loop.run_until_complete(sm.handle_event('lose', ctx))
    assert ctx.get('reset')

def test_parallel_regions(event_loop):
    sm = StateMachine('idle', loop=event_loop)
    sub1 = StateMachine('s1', loop=event_loop)
    sub1.add_state('s1')
    sub1.add_state('s2')
    sub1.add_transition('s1','e','s2')
    sm.define_parallel_regions('r1', sub1)
    # main stays same, region should transition
    event_loop.run_until_complete(sm.handle_event('e'))
    assert sub1.current_state == 's2'

def test_cli_scaffold(capsys):
    old = sys.argv
    sys.argv = ['prog','scaffold','--name','test']
    cli.main()
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data['name']=='test'
    sys.argv = old

def test_cli_simulate(capsys):
    old = sys.argv
    sys.argv = ['prog','simulate','--steps','5']
    cli.main()
    captured = capsys.readouterr()
    assert 'Simulating route with 5 steps' in captured.out
    sys.argv = old

def test_cli_export(capsys):
    old = sys.argv
    sys.argv = ['prog','export','--output','o.txt']
    cli.main()
    captured = capsys.readouterr()
    assert 'Exporting graph to o.txt' in captured.out
    sys.argv = old
