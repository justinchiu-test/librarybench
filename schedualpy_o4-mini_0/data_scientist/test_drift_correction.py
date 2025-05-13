import datetime
from scheduler import Scheduler, Task

def test_drift_correction_baseline():
    # Since drift correction is minimal, ensure missed schedule runs once
    sched = Scheduler()
    def dummy(): pass
    t = Task('d1', dummy).set_cron('0 0 * * *', jitter=0)
    sched.register_cron_task(t)
    # simulate last run was 2 days ago
    past = datetime.datetime.now() - datetime.timedelta(days=2)
    sched.last_cron_run['d1'] = past.replace(hour=0, minute=0, second=0, microsecond=0)
    # current is midnight
    sched.schedule_cron_tasks()
    # should schedule for today only
    assert len(Scheduler.shared_queue) == 1
