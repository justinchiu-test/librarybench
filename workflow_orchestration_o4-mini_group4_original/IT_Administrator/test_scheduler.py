import pytest
import datetime
import time
from IT_Administrator.it_manager.scheduler import Scheduler
from IT_Administrator.it_manager.tasks import Task
from IT_Administrator.it_manager.alert import AlertManager
from IT_Administrator.it_manager.exceptions import TaskTimeoutError

# sample task that records runs
runs = []

def sample(a):
    runs.append(a)

def test_schedule_run_pending_once():
    AlertManager.clear_alerts()
    runs.clear()
    sched = Scheduler()
    t = Task(lambda x: runs.append(x), name="app", timeout=1)
    # schedule to run immediately
    sched.schedule(t, args=(1,), run_at=datetime.datetime.utcnow(), interval=None)
    sched.run_pending()
    assert runs == [1]
    # not run again
    sched.run_pending()
    assert runs == [1]

def test_schedule_with_interval():
    runs.clear()
    sched = Scheduler()
    t = Task(lambda x: runs.append(x), name="app2", timeout=1)
    now = datetime.datetime.utcnow()
    sched.schedule(t, args=(5,), run_at=now, interval=0.1)
    # run multiple intervals manually
    sched.run_pending()
    time.sleep(0.11)
    sched.run_pending()
    time.sleep(0.11)
    sched.run_pending()
    assert runs == [5,5,5]

def test_scheduler_alert_on_failure():
    AlertManager.clear_alerts()
    runs.clear()
    def bad():
        raise RuntimeError("bad")
    t = Task(bad, name="bad", timeout=1)
    sched = Scheduler()
    sched.schedule(t, run_at=datetime.datetime.utcnow())
    sched.run_pending()
    alerts = AlertManager.get_alerts()
    assert len(alerts) == 1
    assert "Job failed" in alerts[0]
