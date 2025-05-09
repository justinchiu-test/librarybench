import pytest
from tasks.core import TaskState, TaskMetadata, TaskContext

def test_taskstate_enum():
    assert TaskState.PENDING.value == "PENDING"
    assert TaskState.SUCCESS in TaskState

def test_metadata_to_dict():
    meta = TaskMetadata("abc")
    meta.start_time = 1.23
    meta.end_time = 4.56
    meta.attempts = 2
    meta.status = TaskState.RUNNING
    meta.error = ValueError("oops")
    d = meta.to_dict()
    assert d["name"] == "abc"
    assert d["status"] == "RUNNING"
    assert d["start_time"] == 1.23
    assert d["end_time"] == 4.56
    assert d["attempts"] == 2
    assert "ValueError" in d["error"]

def test_context_set_get():
    ctx = TaskContext()
    assert ctx.get("x") is None
    ctx.set("x", 42)
    assert ctx.get("x") == 42
    assert ctx.to_dict() == {"x": 42}
