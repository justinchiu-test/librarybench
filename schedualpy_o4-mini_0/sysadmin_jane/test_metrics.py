from scheduler import ThreadSafeScheduler

def test_metrics_exist():
    sched = ThreadSafeScheduler()
    assert hasattr(sched, 'job_runs')
    assert hasattr(sched, 'job_failures')
    assert hasattr(sched, 'job_latency')
