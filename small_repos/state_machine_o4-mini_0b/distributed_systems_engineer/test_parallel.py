import pytest
import asyncio
from fsm.fsm import FSM

@pytest.mark.asyncio
async def test_parallel_regions():
    fsm = FSM('root')
    r1 = FSM('A0')
    r2 = FSM('B0')
    r1.add_transition('A0', 'go', 'A1')
    r2.add_transition('B0', 'go', 'B1')
    fsm.add_region('r1', r1)
    fsm.add_region('r2', r2)
    await fsm.trigger('go')
    assert r1.state == 'A1'
    assert r2.state == 'B1'
