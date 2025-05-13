import pytest
import asyncio
from fsm.fsm import FSM

@pytest.mark.asyncio
async def test_timeout_transition():
    fsm = FSM('init')
    fsm.timeout_transition('wait', 0.05, 'timeout', 'failed')
    fsm.add_transition('init', 'start', 'wait')
    fsm.add_transition('wait', 'timeout', 'failed')
    await fsm.trigger('start')
    await asyncio.sleep(0.1)
    assert fsm.state == 'failed'
