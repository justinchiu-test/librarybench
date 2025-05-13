import asyncio
import inspect

def stub_event(name):
    return {'name': name}

async def drive_sequence(machine, events):
    for e in events:
        if isinstance(e, dict) and 'name' in e:
            await machine.trigger(e['name'])
        else:
            await machine.trigger(e)

def assert_state(machine, expected_state):
    if machine.current_state != expected_state:
        raise AssertionError(f"Expected state {expected_state}, got {machine.current_state}")

def mock_callback():
    calls = []
    def _callback(*args, **kwargs):
        calls.append((args, kwargs))
    _callback.calls = calls
    return _callback

async def run_parallel(machines, events_map):
    tasks = []
    for m in machines:
        events = events_map.get(m, [])
        tasks.append(asyncio.create_task(drive_sequence(m, events)))
    await asyncio.gather(*tasks)

# Scenario registry for CLI
_scenarios = {}

def register_scenario(name):
    def decorator(func):
        _scenarios[name] = func
        return func
    return decorator

def get_scenarios():
    return _scenarios

async def run_scenario(name):
    if name not in _scenarios:
        raise ValueError(f"Scenario {name} not found")
    result = _scenarios[name]()
    if inspect.iscoroutine(result) or inspect.isawaitable(result):
        return await result
    return result

@register_scenario('sample')
def sample_scenario():
    return 'sample_result'

# expose module under its own name for imports like __import__('simulation_helpers').simulation_helpers
import sys
simulation_helpers = sys.modules[__name__]
