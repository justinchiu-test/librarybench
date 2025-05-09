import pytest
from project_manager.task import Task, TaskState
from project_manager.runner import TaskRunner

def test_dynamic_task_creation():
    runner = TaskRunner()
    def parent(ctx):
        # create a child task
        def child(c):
            return "child-result"
        child_task = Task("child", child)
        ctx.add_task(child_task)
        return "parent-done"
    p = Task("parent", parent)
    runner.add_task(p)
    runner.run_all()
    # both tasks should run
    tasks = {t.name: t for t in runner.tasks}
    assert tasks["parent"].state == TaskState.SUCCESS
    assert tasks["child"].state == TaskState.SUCCESS
    # results in context
    out_parent = runner.executor  # dummy
    md_p = runner.metadata.get("parent")
    md_c = runner.metadata.get("child")
    assert md_p["state"] == "success"
    assert md_c["state"] == "success"
