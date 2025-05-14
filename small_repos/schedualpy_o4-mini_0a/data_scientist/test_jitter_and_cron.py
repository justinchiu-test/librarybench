import datetime
from scheduler import Scheduler, Task

def test_cron_without_jitter():
    sched = Scheduler()
    def dummy(): pass
    t = Task('daily', dummy).set_cron('0 0 * * *', jitter=0)
    sched.register_cron_task(t)
    now = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    # monkey-patch now
    sched.last_cron_run.clear()
    # simulate schedule
    sched.schedule_cron_tasks()
    # one entry with run_time equal now
    assert len(Scheduler.shared_queue) == 1
    run_time, task = Scheduler.shared_queue.pop(0)
    assert task is t
    assert run_time == now

def test_cron_with_jitter():
    sched = Scheduler()
    def dummy(): pass
    t = Task('jitter', dummy).set_cron('0 0 * * *', jitter=10)
    sched.register_cron_task(t)
    # ensure match
    sched.last_cron_run.clear()
    sched.schedule_cron_tasks()
    run_time, _ = Scheduler.shared_queue.pop(0)
    delta = (run_time - datetime.datetime.now()).total_seconds()
    assert 0 <= delta <= 10
