import pytest
import asyncio
from datetime import datetime, timedelta

from DevOps_Engineer.src.scheduler import Task, Workflow, WorkflowManager, TaskQueue, Scheduler

@pytest.mark.asyncio
async def test_task_success():
    """A simple task completes successfully without retries."""
    result_holder = {}

    def sample_task():
        result_holder['val'] = 42
        return "ok"

    t = Task(name="t1", func=sample_task, timeout=1, max_retries=0)
    queue = TaskQueue(num_workers=1)
    queue.start_workers()

    # Run directly
    res = await t.run("wf", 1, "run1")
    assert res == "ok"
    assert result_holder['val'] == 42

    await queue.stop_workers()

@pytest.mark.asyncio
async def test_task_timeout_and_no_retry():
    """Task exceeds timeout and does not retry."""
    async def long_task():
        await asyncio.sleep(0.2)
        return "done"

    t = Task(name="t_timeout", func=long_task, timeout=0.1, max_retries=0, retry_delay_seconds=0.01)
    with pytest.raises(asyncio.TimeoutError):
        await t.run("wf", 1, "run2")

@pytest.mark.asyncio
async def test_task_retries_and_backoff(monkeypatch):
    """Task fails twice then succeeds, ensure retries and exponential backoff."""
    calls = []

    def flaky():
        calls.append(datetime.utcnow())
        if len(calls) < 3:
            raise ValueError("fail")
        return "success"

    t = Task(name="t_flaky", func=flaky, timeout=1, max_retries=2, retry_delay_seconds=0.01)
    start = datetime.utcnow()
    res = await t.run("wf", 1, "run3")
    assert res == "success"
    # Ensure we had at least 3 calls
    assert len(calls) == 3
    # Check exponential backoff roughly: second error backoff ~0.01s, next ~0.02s
    intervals = [(calls[i] - calls[i-1]).total_seconds() for i in range(1, len(calls))]
    assert intervals[0] >= 0  # initial immediate retry
    assert intervals[1] >= 0.01

@pytest.mark.asyncio
async def test_dependency_order():
    """Ensure tasks run in proper dependency order."""
    order = []

    def task_a():
        order.append("A")
    def task_b():
        order.append("B")
    def task_c():
        order.append("C")

    t_a = Task(name="A", func=task_a)
    t_b = Task(name="B", func=task_b, dependencies=["A"])
    t_c = Task(name="C", func=task_c, dependencies=["B"])
    wf = Workflow(name="w1", version=1, tasks={"A": t_a, "B": t_b, "C": t_c})
    queue = TaskQueue(num_workers=1)
    queue.start_workers()
    run_id = await wf.run(queue)
    # Wait for queue to finish
    await asyncio.sleep(0.1)
    await queue.stop_workers()
    assert order == ["A", "B", "C"]

@pytest.mark.asyncio
async def test_workflow_scheduling_once():
    """Test manual scheduling of due workflows."""
    # Task that marks it ran
    ran = {"x": False}

    def task_x():
        ran["x"] = True

    t_x = Task(name="X", func=task_x)
    wf = Workflow(name="timer", version=1, tasks={"X": t_x}, schedule_interval_seconds=0.01)
    manager = WorkflowManager()
    manager.add_workflow_version(wf)
    queue = TaskQueue(num_workers=1)
    scheduler = Scheduler(manager, queue, tick_seconds=0.005)
    queue.start_workers()
    # Initially next_run is now+interval, so not due yet
    await scheduler.schedule_due_workflows()
    assert not ran["x"]
    # Fast-forward next_run
    wf.next_run = datetime.utcnow() - timedelta(seconds=1)
    await scheduler.schedule_due_workflows()
    # Allow execution
    await asyncio.sleep(0.05)
    assert ran["x"]
    await queue.stop_workers()
