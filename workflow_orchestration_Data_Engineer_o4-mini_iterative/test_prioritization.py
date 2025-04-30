import time
from pipeline.auth import Auth
from pipeline.scheduler import Scheduler
from pipeline.tasks import Task

def test_higher_priority_runs_first():
    auth = Auth()
    auth.add_user('u', 'pwd', roles=['user'])
    token = auth.login('u', 'pwd')
    sched = Scheduler(auth)

    order = []
    def make_fn(name):
        return lambda: order.append(name)

    low = Task("low", make_fn("low"), priority=1)
    high = Task("high", make_fn("high"), priority=10)

    for t in (low, high):
        t.next_run_time = time.time() - 1
        sched.add_task(t, token)

    sched.run_pending(token)
    assert order == ["high", "low"]
