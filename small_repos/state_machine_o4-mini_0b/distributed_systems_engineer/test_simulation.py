import pytest
import asyncio
from fsm.fsm import FSM
from fsm.simulation import Simulator

@pytest.mark.asyncio
async def test_simulation_harness():
    fsm = FSM('S')
    fsm.add_transition('S', 'go', 'T')
    sim = Simulator(fsm)
    sim.feed('go')
    final = await sim.run()
    assert final == 'T'
