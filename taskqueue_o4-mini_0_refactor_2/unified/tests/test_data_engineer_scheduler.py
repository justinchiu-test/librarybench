import datetime
from data_engineer.etl.scheduler import DelayedTaskScheduling
from data_engineer.etl.taskchain import Task

def test_scheduling_and_due_tasks():
    ds = DelayedTaskScheduling()
    now = datetime.datetime.now()
    past = now - datetime.timedelta(seconds=1)
    future = now + datetime.timedelta(seconds=1)
    t1 = Task("t1", lambda: None)
    t2 = Task("t2", lambda: None)
    ds.schedule(t1, past)
    ds.schedule(t2, future)
    due = ds.get_due_tasks(now)
    assert t1 in due
    remaining = ds.get_due_tasks(now)
    assert t2 not in due
    # after time advances
    due2 = ds.get_due_tasks(future + datetime.timedelta(seconds=1))
    assert t2 in due2
