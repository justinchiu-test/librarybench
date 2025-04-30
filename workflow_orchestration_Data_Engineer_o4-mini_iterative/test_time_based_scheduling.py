import time
from pipeline.auth import Auth
from pipeline.scheduler import Scheduler
from pipeline.tasks import Task

def test_task_not_run_before_scheduled_time():
    auth = Auth()
    auth.add_user('sch', 'pwd', roles=['user'])
    token = auth.login('sch', 'pwd')
    sched = Scheduler(auth)

    executed = []
    def fn():
        executed.append(True)

    future = Task("future", fn)
    future.next_run_time = time.time() + 2  # 2 seconds in future
    sched.add_task(future, token)

    sched.run_pending(token)
    assert executed == []

    # Simulate time passing
    future.next_run_time = time.time() - 1
    sched.run_pending(token)
    assert executed == [True]
