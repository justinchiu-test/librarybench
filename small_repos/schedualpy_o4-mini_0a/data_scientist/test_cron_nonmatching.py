import datetime
from scheduler import Scheduler, Task

def test_cron_nonmatching_time():
    sched = Scheduler()
    def dummy(): pass
    t = Task('no', dummy).set_cron('0 0 * * *', jitter=0)
    sched.register_cron_task(t)
    # simulate non-midnight by monkey patching _match_cron
    sched._match_cron = lambda cron, now: False
    sched.schedule_cron_tasks()
    assert len(Scheduler.shared_queue) == 0
