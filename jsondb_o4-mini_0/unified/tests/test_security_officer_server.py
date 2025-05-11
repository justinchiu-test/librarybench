import pytest
import os
import json
from security_officer.auditdb.db import AuditDB
from security_officer.auditdb.server import create_app

@pytest.fixture
def client(tmp_path):
    key = b"1" * 32
    dbdir = tmp_path / "db2"
    dbdir.mkdir()
    db = AuditDB(str(dbdir), key, ttl_days=10)
    app = create_app(db)
    app.config["TESTING"] = True
    return app.test_client()

def test_post_and_get_logs(client):
    rec = {
        "auditID": "s1",
        "userID": "u1",
        "eventSeverity": "LOW",
        "timestamp": "2020-01-01T00:00:00",
        "message": "hello"
    }
    # unauthorized
    rv = client.post("/logs", json=[rec], headers={"Role": "guest"})
    assert rv.status_code == 403
    # authorized
    rv = client.post("/logs", json=[rec], headers={"Role": "auditor"})
    assert rv.status_code == 201
    # get
    rv = client.get("/logs", query_string={"userID": "u1"})
    data = rv.get_json()
    assert isinstance(data, list) and data[0]["auditID"] == "s1"

def test_soft_delete_endpoint(client):
    rec = {
        "auditID": "s2",
        "userID": "u2",
        "eventSeverity": "MEDIUM",
        "timestamp": "2020-01-02T00:00:00",
        "message": "msg"
    }
    client.post("/logs", json=[rec], headers={"Role": "admin"})
    rv = client.post("/logs/soft_delete", json={"auditID": "s2"}, headers={"Role": "auditor"})
    assert rv.status_code == 200
    rv2 = client.get("/logs", query_string={"status": "archived"})
    data = rv2.get_json()
    assert data and data[0]["status"] == "archived"

def test_hard_delete_endpoint(client):
    rec = {
        "auditID": "s3",
        "userID": "u3",
        "eventSeverity": "CRITICAL",
        "timestamp": "2020-01-03T00:00:00",
        "message": "msg3"
    }
    client.post("/logs", json=[rec], headers={"Role": "admin"})
    # forbidden for auditor
    rv = client.post("/logs/delete", json={"auditID": "s3"}, headers={"Role": "auditor"})
    assert rv.status_code == 403
    # allowed for admin
    rv2 = client.post("/logs/delete", json={"auditID": "s3"}, headers={"Role": "admin"})
    assert rv2.status_code == 200
    rv3 = client.get("/logs")
    assert rv3.get_json() == []
