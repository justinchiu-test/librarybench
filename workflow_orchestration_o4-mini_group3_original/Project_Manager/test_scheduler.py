import time
from Project_Manager.core.scheduler import Scheduler
from Project_Manager.core.workflow import Workflow
from Project_Manager.core.task import Task, TaskStatus

def test_scheduler_runs_interval():
    outputs = []
    wf = Workflow("swf")
    wf.add_task(Task("T", func=lambda: outputs.append(time.time()), timeout=1))
    sched = Scheduler()
    sched.schedule_workflow(wf, interval_seconds=0.3)
    time.sleep(0.7)
    sched.stop_all()
    # Should have run at least twice
    assert len(outputs) >= 2
    assert wf.last_status == TaskStatus.SUCCESS
