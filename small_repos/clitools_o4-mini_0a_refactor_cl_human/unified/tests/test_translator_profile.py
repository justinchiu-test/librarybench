import time
from src.personas.translator.profile import Profiler

def test_profile_command_measures_time():
    # Create a profiler
    profiler = Profiler()
    
    # Define two steps to measure
    def step_fast():
        return "fast result"
    
    def step_slow():
        time.sleep(0.01)
        return "slow result"
    
    # Measure the fast step
    profiler.start("fast")
    step_fast()
    profiler.stop("fast")
    
    # Measure the slow step
    profiler.start("slow")
    step_slow()
    profiler.stop("slow")
    
    # Get results
    results = profiler.get_stats()
    
    # Verify results
    assert 'fast' in results
    assert 'slow' in results
    assert results['fast']['total'] >= 0
    assert results['slow']['total'] >= 0.01