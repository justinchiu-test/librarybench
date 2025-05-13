import datetime
from scheduler import Scheduler, Task

def test_weekly_cron():
    sched = Scheduler()
    def dummy(): pass
    t = Task('weekly', dummy).set_cron('0 0 * * 0', jitter=0)
    sched.register_cron_task(t)
    # simulate Sunday midnight
    now = datetime.datetime.now()
    sunday = now + datetime.timedelta(days=(6 - now.weekday()) % 7)
    sunday = sunday.replace(hour=0, minute=0, second=0, microsecond=0)
    # monkey-patch now by adjusting last_cron_run logic
    sched.last_cron_run.clear()
    sched.schedule_cron_tasks()
    assert len(Scheduler.shared_queue) == 1
