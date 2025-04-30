import time
import pytest
from pipeline.auth import Auth
from pipeline.scheduler import Scheduler, SchedulerError
from pipeline.tasks import Task, TaskState

def test_add_task_unauthorized():
    auth = Auth()
    auth.add_user('no_role', 'pwd', roles=[])
    token = auth.login('no_role', 'pwd')
    sched = Scheduler(auth)
    task = Task("t", lambda: None)
    with pytest.raises(SchedulerError):
        sched.add_task(task, token)

def test_run_pending_unauthorized():
    auth = Auth()
    auth.add_user('no_role', 'pwd', roles=[])
    token = auth.login('no_role', 'pwd')
    sched = Scheduler(auth)
    with pytest.raises(SchedulerError):
        sched.run_pending(token)

def test_add_and_run_task_success():
    auth = Auth()
    auth.add_user('operator', 'pwd', roles=['user'])
    token = auth.login('operator', 'pwd')
    sched = Scheduler(auth)

    executed = []
    def fn():
        executed.append(True)
    task = Task("t1", fn)
    task.next_run_time = time.time() - 1
    sched.add_task(task, token)
    sched.run_pending(token)

    assert executed == [True]
    assert task.state == TaskState.SUCCESS
