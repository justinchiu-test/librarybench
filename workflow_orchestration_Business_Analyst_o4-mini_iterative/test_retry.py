import pytest
from automation.core import Task, WorkflowManager
from automation.notifier import Notifier
from automation.logger import AuditLogger
from automation.security import SecurityManager

def test_task_retries_and_eventual_success():
    notifier = Notifier()
    logger = AuditLogger()
    security = SecurityManager()
    wm = WorkflowManager(notifier, logger, security)

    state = {"count": 0}
    def flaky(ctx):
        state["count"] += 1
        if state["count"] < 3:
            raise RuntimeError("fail")
        return "ok"

    task = Task(name="flaky", func=flaky, retries=3)
    wm.add_task(task)
    wm.run_pending()
    assert wm.context["flaky"] == "ok"
    # Should have attempted 3 times
    start_logs = [e for (_, e) in logger.logs if "started" in e]
    assert len(start_logs) == 3

def test_task_exhaust_retries_and_fail():
    notifier = Notifier()
    logger = AuditLogger()
    security = SecurityManager()
    wm = WorkflowManager(notifier, logger, security)

    def always_fail(ctx):
        raise ValueError("bad")

    task = Task(name="badtask", func=always_fail, retries=1)
    wm.add_task(task)
    wm.run_pending()
    # Context should not have 'badtask'
    assert "badtask" not in wm.context
    # Final status is 'failed'
    assert task.status == 'failed'
    # Notifier should have failure messages
    failures = [m for m in notifier.notifications if "failed" in m]
    assert any("badtask failed" in m for m in failures)
