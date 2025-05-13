import pytest
from iotscheduler.api import app, scheduler
from datetime import datetime, timedelta
import json

@pytest.fixture
def client():
    return app.test_client()

def test_create_and_list_and_delete_oneoff(client):
    # create
    resp = client.post("/tasks/oneoff", json={"delay": 0.01})
    assert resp.status_code == 201
    data = resp.get_json()
    tid = data["task_id"]
    # list
    resp2 = client.get("/tasks")
    tasks = resp2.get_json()
    assert tid in tasks
    # delete
    resp3 = client.delete(f"/tasks/{tid}")
    assert resp3.status_code == 204
    resp4 = client.get("/tasks")
    tasks2 = resp4.get_json()
    assert tid not in tasks2

def test_reschedule_not_found(client):
    resp = client.post("/tasks/nonexistent/reschedule", json={"interval": 1})
    assert resp.status_code == 404

def test_reschedule_existing(client):
    # create one-off
    resp = client.post("/tasks/oneoff", json={"delay": 0.01})
    tid = resp.get_json()["task_id"]
    # attempt to reschedule as interval => should 404 or no-op
    resp2 = client.post(f"/tasks/{tid}/reschedule", json={"interval": 0.05})
    # one-off cannot be interval, but dynamic_reschedule will KeyError
    assert resp2.status_code == 404 or resp2.status_code == 204
