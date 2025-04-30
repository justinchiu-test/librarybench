import time
from pipeline.auth import Auth
from pipeline.scheduler import Scheduler
from pipeline.tasks import Task, TaskState

def test_dynamic_task_creation_and_execution():
    auth = Auth()
    auth.add_user('dyn', 'pwd', roles=['user'])
    token = auth.login('dyn', 'pwd')
    sched = Scheduler(auth)

    # Parent task that creates one child
    def parent_fn():
        child = Task("child", lambda: "child_ok")
        return [child]

    parent = Task("parent", parent_fn)
    parent.next_run_time = time.time() - 1
    sched.add_task(parent, token)

    sched.run_pending(token)
    # Parent should succeed, child should also be added and run
    child = sched.tasks.get("child")
    assert child is not None
    assert child.state == TaskState.SUCCESS
