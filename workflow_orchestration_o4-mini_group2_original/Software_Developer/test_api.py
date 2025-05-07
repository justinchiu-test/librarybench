import time
import pytest
from Software_Developer.task_manager.api import app, workflow_manager, scheduler, task_queue

@pytest.fixture(autouse=True)
def cleanup():
    # Clear any previous state
    workflow_manager.workflows.clear()
    yield
    # Stop background threads
    try:
        scheduler.stop()
    except:
        pass
    try:
        task_queue.stop()
    except:
        pass

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as c:
        yield c

def test_create_and_list(client):
    rv = client.get("/workflows")
    assert rv.status_code == 200 and rv.get_json() == []
    rv = client.post("/workflows", json={"name":"W1"})
    assert rv.status_code == 200
    assert rv.get_json()["version"] == 1
    rv2 = client.get("/workflows")
    assert {"name":"W1","version":1} in rv2.get_json()

def test_run_and_schedule_endpoints(client):
    client.post("/workflows", json={"name":"W2"})
    rv = client.post("/workflows/W2/run")
    assert rv.status_code == 200 and rv.get_json()["status"]=="scheduled"
    rv = client.post("/workflows/W2/schedule", json={"interval":0.1})
    assert rv.status_code == 200 and rv.get_json()["interval"]==0.1
    # allow a couple runs
    time.sleep(0.3)
