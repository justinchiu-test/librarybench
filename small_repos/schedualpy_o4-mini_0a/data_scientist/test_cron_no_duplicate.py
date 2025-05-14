import datetime
from scheduler import Scheduler, Task

def test_no_duplicate_cron_run():
    sched = Scheduler()
    def dummy(): pass
    t = Task('once', dummy).set_cron('0 0 * * *', jitter=0)
    sched.register_cron_task(t)
    sched.last_cron_run.clear()
    sched.schedule_cron_tasks()
    first = list(Scheduler.shared_queue)
    sched.schedule_cron_tasks()
    second = list(Scheduler.shared_queue)
    # no new entries on second call at same time
    assert first == second
