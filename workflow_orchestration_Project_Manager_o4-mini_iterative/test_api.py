import pytest
from api.app import app, workflows
from core.workflow import Workflow
from core.task import Task, TaskStatus

@pytest.fixture
def client():
    # Setup example workflow
    workflows.clear()
    wf = Workflow("apiwf")
    wf.add_task(Task("T", func=lambda: None, timeout=1))
    workflows["apiwf"] = wf
    with app.test_client() as client:
        yield client

def test_run_and_status(client):
    rv = client.post("/workflows/apiwf/run")
    assert rv.status_code == 202
    # Give queue time to process
    import time; time.sleep(0.1)
    rv = client.get("/workflows/apiwf/status")
    assert rv.status_code == 200
    data = rv.get_json()
    assert data["name"] == "apiwf"
    assert data["last_status"] == TaskStatus.SUCCESS

def test_unknown_workflow(client):
    rv = client.post("/workflows/nonexist/run")
    assert rv.status_code == 404
    rv = client.get("/workflows/nonexist/status")
    assert rv.status_code == 404
