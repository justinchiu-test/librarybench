import pytest
from automation.core import Task, WorkflowManager
from automation.notifier import Notifier
from automation.logger import AuditLogger
from automation.security import SecurityManager, PermissionError

def test_simple_task_execution_and_context():
    notifier = Notifier()
    logger = AuditLogger()
    security = SecurityManager()
    wm = WorkflowManager(notifier, logger, security)

    # define a task
    def foo(ctx):
        return 42

    task = Task(name="foo", func=foo)
    wm.add_task(task)
    wm.run_pending()
    # After run, context has foo
    assert wm.context["foo"] == 42
    # Notifications include start and success
    msgs = notifier.notifications
    assert "Task foo started" in msgs
    assert "Task foo succeeded" in msgs

def test_task_required_role_blocks_execution():
    notifier = Notifier()
    logger = AuditLogger()
    security = SecurityManager()
    security.add_user("carol", roles=["viewer"])
    security.authenticate("carol")
    wm = WorkflowManager(notifier, logger, security)

    def secure_task(ctx):
        return "secret"

    task = Task(name="secure", func=secure_task, required_role="admin")
    wm.add_task(task)
    wm.run_pending()
    # Should not run; context empty
    assert "secure" not in wm.context
    # Log contains permission error
    events = [e for (_, e) in logger.logs]
    assert any("permission error" in e for e in events)
