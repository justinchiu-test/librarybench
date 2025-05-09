import pytest
from tasks.manager import Task, TaskManager

def test_dynamic_task_creation():
    def creator(ctx, inputs):
        manager = ctx.get("manager")
        # create a new task that doubles the number
        def double(ctx2, inputs2):
            val = ctx2.get("value", 0)
            return {"doubled": val * 2}
        # set a value in context
        ctx.set("value", inputs["start"])
        manager.add_task(Task(name="double", func=double))
        return {"created": True}

    tm = TaskManager()
    creator_task = Task(name="creator", func=creator, inputs={"start": 5})
    tm.add_task(creator_task)
    results = tm.run_all()
    # Both tasks should have run
    assert "creator" in results and results["creator"] == {"created": True}
    assert "double" in results and results["double"] == {"doubled": 10}

    # Ensure metadata tracking
    assert tm.metadata["creator"].status.value == "SUCCESS"
    assert tm.metadata["double"].status.value == "SUCCESS"
