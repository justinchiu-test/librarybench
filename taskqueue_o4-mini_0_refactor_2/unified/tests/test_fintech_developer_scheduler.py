import time
from fintech_developer.scheduler import Scheduler

def test_scheduler_run_due():
    results = []
    def task(x):
        results.append(x)
    sched = Scheduler()
    # schedule past and future
    sched.schedule(time.time() - 1, task, 1)
    sched.schedule(time.time() + 10, task, 2)
    sched.run_due()
    assert results == [1]
    sched.run_all()
    assert results == [1, 2]
