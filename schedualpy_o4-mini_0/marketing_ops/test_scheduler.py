import datetime
import time
from datetime import timedelta
from scheduler.scheduler import Scheduler, Task
import scheduler.utils as utils

def test_one_off_task_execution():
    sched = Scheduler()
    executed = []
    def action(ctx):
        executed.append(ctx['task'].name)
    now = datetime.datetime.now()
    task = Task(name="oneoff", action=action, schedule=now)
    sched.register_task(task)
    due = sched.run_pending()
    assert "oneoff" in executed
    assert sched.get_metrics()['executed'] == 1

def test_concurrency_limit():
    sched = Scheduler()
    executed = []
    def action(ctx):
        executed.append(ctx['task'].name)
    sched.set_concurrency_limit(region='us', channel='email', limit=1)
    now = datetime.datetime.now()
    t1 = Task(name="t1", action=action, schedule=now, region='us', channel='email')
    t2 = Task(name="t2", action=action, schedule=now, region='us', channel='email')
    sched.register_task(t1)
    sched.register_task(t2)
    due = sched.run_pending()
    assert len(executed) == 1
    assert sched.get_metrics()['executed'] == 1
    assert sched.get_metrics()['skipped'] == 1

def test_recurring_cron_task(monkeypatch):
    sched = Scheduler()
    executed = []
    def action(ctx):
        executed.append(ctx['task'].name)
    monkeypatch.setattr(utils, 'next_run_cron',
                        lambda cron, base_time=None, jitter_seconds=0: datetime.datetime.now() + timedelta(seconds=1))
    task = Task(name="cron", action=action, cron="* * * * *", recurring=True)
    sched.register_task(task)
    due = sched.run_pending()
    assert executed == ['cron']
    assert len(sched.tasks) >= 1
    time.sleep(1.1)
    due2 = sched.run_pending()
    assert executed == ['cron', 'cron']
