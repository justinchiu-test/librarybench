from Business_Analyst.automation.core import Task, WorkflowManager
from Business_Analyst.automation.notifier import Notifier
from Business_Analyst.automation.logger import AuditLogger
from Business_Analyst.automation.security import SecurityManager

def test_task_skipped_when_condition_false():
    notifier = Notifier()
    logger = AuditLogger()
    security = SecurityManager()
    wm = WorkflowManager(notifier, logger, security)

    def never_run(ctx):
        return "run"

    # condition always false
    task = Task(name="never", func=never_run, condition=lambda ctx: False)
    wm.add_task(task)
    wm.run_pending()
    assert "never" not in wm.context
    # log should mention skipped
    assert any("skipped" in e for (_, e) in logger.logs)
