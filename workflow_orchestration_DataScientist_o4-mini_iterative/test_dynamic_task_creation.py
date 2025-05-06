import pytest
from pipeline.task import Task
from pipeline.pipeline import Pipeline

class CreatorTask(Task):
    def run(self, context):
        # create a dynamic task
        class Dyn(Task):
            def run(self, ctx):
                return "dyn"
        dyn = Dyn("dyn1")
        context.add_dynamic_task(dyn)
        return "created"

def test_dynamic_creation():
    p = Pipeline()
    p.add_task(CreatorTask("creator"))
    ctx = p.run()
    # both tasks should have run
    assert ctx.get("creator") == "created"
    assert ctx.get("dyn1") == "dyn"
    # metadata should include both
    task_ids = [r['task_id'] for r in p.metadata.records]
    assert "creator" in task_ids
    assert "dyn1" in task_ids
