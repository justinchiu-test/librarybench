import datetime
from data_engineer.etl.multitenancy import MultiTenancySupport
from data_engineer.etl.taskchain import TaskChaining
from data_engineer.etl.scheduler import DelayedTaskScheduling
from data_engineer.etl.audit import AuditLogging
from data_engineer.etl.cli import CLIInterface

def test_cli_launch_inspect_cancel_and_logs():
    mts = MultiTenancySupport()
    mts.create_tenant("teamA")
    tc = TaskChaining()
    sched = DelayedTaskScheduling()
    audit = AuditLogging()
    cli = CLIInterface(mts, tc, sched, audit)
    eta = datetime.datetime.now() + datetime.timedelta(seconds=0)
    # launch
    t = cli.launch_job("teamA", "job1", lambda: None, eta=eta)
    queue = cli.inspect_queue("teamA")
    assert any(task.id == "job1" for task in queue)
    # cancel
    canceled = cli.cancel_task("job1")
    assert canceled
    # logs
    logs = cli.tail_logs(5)
    assert any(e["event"] == "enqueue" and e["task_id"] == "job1" for e in logs)
    assert any(e["event"] == "cancel" and e["task_id"] == "job1" for e in logs)
