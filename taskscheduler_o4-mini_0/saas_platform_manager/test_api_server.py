import json
import pytest
from scheduler import Scheduler
from api_server import create_app

@pytest.fixture
def client():
    sched = Scheduler()
    # create some jobs
    j1 = sched.schedule_job("t1", {"a": 1})
    j2 = sched.schedule_job("t1", {"b": 2})
    app = create_app(sched)
    app.config['TESTING'] = True
    return app.test_client(), sched, j1, j2

def test_list_jobs(client):
    c, sched, j1, j2 = client
    resp = c.get(f"/jobs/t1")
    assert resp.status_code == 200
    data = resp.get_json()
    ids = {item["job_id"] for item in data}
    assert {j1, j2} == ids

def test_pause_resume_cancel_remove(client):
    c, sched, j1, _ = client
    resp = c.post(f"/jobs/{j1}/pause")
    assert resp.status_code == 204
    assert sched.jobs[j1].status == "paused"
    resp = c.post(f"/jobs/{j1}/resume")
    assert resp.status_code == 204
    assert sched.jobs[j1].status == "scheduled"
    resp = c.post(f"/jobs/{j1}/cancel")
    assert resp.status_code == 204
    assert sched.jobs[j1].status == "cancelled"
    resp = c.delete(f"/jobs/{j1}")
    assert resp.status_code == 204
    assert j1 not in sched.jobs

def test_set_concurrency_and_priority(client):
    c, sched, j1, _ = client
    resp = c.post(f"/jobs/{j1}/concurrency", data=json.dumps({"limit": 3}), content_type='application/json')
    assert resp.status_code == 204
    assert sched.jobs[j1].concurrency_limit == 3
    resp = c.post(f"/jobs/{j1}/priority", data=json.dumps({"level": 9}), content_type='application/json')
    assert resp.status_code == 204
    assert sched.jobs[j1].priority == 9

def test_set_global_concurrency(capsys):
    sched = Scheduler()
    app = create_app(sched)
    client = app.test_client()
    resp = client.post("/global/concurrency", data=json.dumps({"limit": 8}), content_type='application/json')
    assert resp.status_code == 204
    assert sched.global_concurrency_limit == 8

def test_dump_load_catchup(client, tmp_path):
    c, sched, j1, _ = client
    # dump
    f = tmp_path / "dump.json"
    resp = c.post("/dump", data=json.dumps({"path": str(f)}), content_type='application/json')
    assert resp.status_code == 204
    # clear and load
    sched.jobs = {}
    resp = c.post("/load", data=json.dumps({"path": str(f)}), content_type='application/json')
    assert resp.status_code == 204
    assert j1 in sched.jobs
    # catchup
    sched.jobs[j1].next_run = sched.jobs[j1].next_run.replace(year=2000)
    resp = c.post("/catchup")
    assert resp.status_code == 204
    assert sched.jobs[j1].missed_runs == 1
