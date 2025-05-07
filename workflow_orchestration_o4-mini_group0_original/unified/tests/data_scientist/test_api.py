import pytest
from unified.ds.api import app

@pytest.fixture
def client():
    app.testing = True
    return app.test_client()

def test_create_and_list_workflow(client):
    resp = client.post("/workflows", json={"name": "api_wf"})
    assert resp.status_code == 201
    data = resp.get_json()
    assert "workflow_id" in data

    resp2 = client.get("/workflows")
    assert resp2.status_code == 200
    lst = resp2.get_json()
    assert any(w["workflow_id"] == data["workflow_id"] for w in lst)

def test_add_task_and_run(client):
    # Create
    resp = client.post("/workflows", json={"name": "api_wf2"})
    wid = resp.get_json()["workflow_id"]

    # Add a simple task
    resp2 = client.post(f"/workflows/{wid}/tasks", json={
        "task_id": "t1",
        "command": "2 + 2"
    })
    assert resp2.status_code == 201

    # Run workflow
    resp3 = client.post(f"/workflows/{wid}/run")
    assert resp3.status_code == 200

def test_schedule_endpoint(client):
    resp = client.post("/workflows", json={"name": "api_wf3"})
    wid = resp.get_json()["workflow_id"]

    resp2 = client.post(f"/workflows/{wid}/schedule", json={"interval_seconds": 10})
    assert resp2.status_code == 200
    assert resp2.get_json()["message"] == "Scheduled"