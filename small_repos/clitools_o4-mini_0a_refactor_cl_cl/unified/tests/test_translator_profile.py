import time
from translator.profile import profile_command

def test_profile_command_measures_time():
    # Define two steps
    def step_fast():
        return
    def step_slow():
        time.sleep(0.01)
    results = profile_command(('fast', step_fast), ('slow', step_slow))
    assert 'fast' in results
    assert 'slow' in results
    assert results['fast'] >= 0
    assert results['slow'] >= 0.01
