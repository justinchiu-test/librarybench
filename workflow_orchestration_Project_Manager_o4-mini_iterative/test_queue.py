import time
from core.queue import TaskQueue
from core.workflow import Workflow
from core.task import Task, TaskStatus

def test_queue_process(monkeypatch):
    outputs = []
    wf = Workflow("qwf")
    wf.add_task(Task("T", func=lambda: outputs.append("X"), timeout=1))
    q = TaskQueue()
    # Run process in background
    q.start()
    q.enqueue(wf)
    time.sleep(0.2)
    q.stop()
    assert outputs == ["X"]
    assert wf.last_status == TaskStatus.SUCCESS
