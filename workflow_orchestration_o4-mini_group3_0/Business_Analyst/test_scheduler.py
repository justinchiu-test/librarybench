import time
from Business_Analyst.automation.core import Task, WorkflowManager
from Business_Analyst.automation.notifier import Notifier
from Business_Analyst.automation.logger import AuditLogger
from Business_Analyst.automation.security import SecurityManager

def test_scheduled_task_runs_only_when_due():
    notifier = Notifier()
    logger = AuditLogger()
    security = SecurityManager()
    wm = WorkflowManager(notifier, logger, security)

    count = {"runs": 0}
    def scheduled(ctx):
        count["runs"] += 1

    # schedule every 0.05 seconds
    task = Task(name="sched", func=scheduled, schedule_interval=0.05)
    wm.add_task(task)
    # First run
    wm.run_pending()
    assert count["runs"] == 1
    # Immediately run again -> not due
    wm.run_pending()
    assert count["runs"] == 1
    # Wait until due again
    time.sleep(0.06)
    wm.run_pending()
    assert count["runs"] == 2
