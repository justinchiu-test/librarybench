from automation.core import Task, WorkflowManager
from automation.notifier import Notifier
from automation.logger import AuditLogger
from automation.security import SecurityManager

def test_tasks_run_in_priority_order():
    notifier = Notifier()
    logger = AuditLogger()
    security = SecurityManager()
    wm = WorkflowManager(notifier, logger, security)

    order = []
    def task1(ctx):
        order.append("first")
    def task2(ctx):
        order.append("second")

    # task2 has higher priority number -> runs later
    t1 = Task(name="t1", func=task1, priority=1)
    t2 = Task(name="t2", func=task2, priority=5)
    wm.add_task(t2)
    wm.add_task(t1)
    wm.run_pending()
    assert order == ["first", "second"]
