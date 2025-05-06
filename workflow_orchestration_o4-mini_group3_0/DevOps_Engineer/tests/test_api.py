import pytest
import asyncio
from DevOps_Engineer.fastapi.testclient import TestClient

from DevOps_Engineer.src.api import app, wf_manager, task_queue

client = TestClient(app)

def setup_module(module):
    # Ensure clean state
    wf_manager._workflows.clear()

def test_list_empty():
    resp = client.get("/workflows")
    assert resp.status_code == 200
    assert resp.json() == {}

def test_trigger_missing():
    resp = client.post("/workflows/foo/run")
    assert resp.status_code == 404

def test_add_and_get_workflow():
    # Manually register a workflow
    from src.scheduler import Workflow, Task
    def f(): return "hi"
    t = Task(name="A", func=f)
    wf = Workflow(name="apiwf", version=1, tasks={"A": t})
    wf_manager.add_workflow_version(wf)

    # Get list
    resp = client.get("/workflows")
    assert resp.status_code == 200
    assert resp.json().get("apiwf") == 1

    # Get details
    resp2 = client.get("/workflows/apiwf")
    assert resp2.status_code == 200
    data = resp2.json()
    assert data["name"] == "apiwf"
    assert data["version"] == 1
    assert "A" in data["tasks"]

def test_run_workflow_api():
    # Using the existing workflow apiwf
    resp = client.post("/workflows/apiwf/run")
    assert resp.status_code == 200
    data = resp.json()
    assert "run_id" in data

def test_rollback_api():
    # Add version 2
    from src.scheduler import Workflow, Task
    def f2(): return "ok"
    t2 = Task(name="B", func=f2)
    wf2 = Workflow(name="apiwf", version=2, tasks={"B": t2})
    wf_manager.add_workflow_version(wf2)
    # Now rollback to version 1
    resp = client.post("/workflows/apiwf/rollback", json={"version": 1})
    assert resp.status_code == 200
    assert wf_manager.list_workflows()["apiwf"] == 1
    # Invalid rollback
    resp2 = client.post("/workflows/apiwf/rollback", json={"version": 99})
    assert resp2.status_code == 404
