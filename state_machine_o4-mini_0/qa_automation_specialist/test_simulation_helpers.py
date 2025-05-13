import pytest
import asyncio
from simulation_helpers import stub_event, drive_sequence, assert_state, mock_callback, run_parallel
from event_system import StateMachine

def test_stub_event():
    ev = stub_event('test')
    assert ev == {'name': 'test'}

@pytest.mark.asyncio
async def test_drive_sequence_and_assert_state():
    sm = StateMachine('A')
    sm.add_transition('go', 'A', 'B')
    events = ['go']
    await drive_sequence(sm, events)
    assert_state = __import__('simulation_helpers').simulation_helpers.assert_state
    assert sm.current_state == 'B'

def test_assert_state_failure():
    sm = StateMachine('A')
    with pytest.raises(AssertionError):
        # direct import to use assert_state
        from simulation_helpers import assert_state
        assert_state(sm, 'B')

def test_mock_callback():
    cb = mock_callback()
    cb(1, key='value')
    assert cb.calls == [((1,), {'key':'value'})]

@pytest.mark.asyncio
async def test_run_parallel():
    sm1 = StateMachine('A')
    sm1.add_transition('go1', 'A', 'B')
    sm2 = StateMachine('X')
    sm2.add_transition('go2', 'X', 'Y')
    events_map = {sm1: ['go1'], sm2: ['go2']}
    await run_parallel([sm1, sm2], events_map)
    assert sm1.current_state == 'B'
    assert sm2.current_state == 'Y'
