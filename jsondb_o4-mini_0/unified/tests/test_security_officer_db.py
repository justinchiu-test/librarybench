import os
import json
import pytest
import tempfile
from datetime import datetime, timedelta

from security_officer.auditdb.db import AuditDB
from security_officer.auditdb.encryption import Encryptor
from security_officer.auditdb.schema import enforce_schema
from security_officer.auditdb.plugins import PluginManager
from security_officer.jsonschema import ValidationError

@pytest.fixture
def tmpdb(tmp_path):
    key = b"0" * 32
    dbdir = tmp_path / "db"
    dbdir.mkdir()
    db = AuditDB(str(dbdir), key, ttl_days=1)
    return db, str(dbdir), key

def make_record(aid, days_offset=0):
    ts = (datetime.utcnow() - timedelta(days=days_offset)).isoformat()
    return {
        "auditID": aid,
        "userID": "user1",
        "eventSeverity": "HIGH",
        "timestamp": ts,
        "message": "Test"
    }

def test_enforce_schema_valid():
    rec = make_record("1")
    assert enforce_schema(rec)

def test_enforce_schema_invalid():
    rec = make_record("1")
    rec["eventSeverity"] = "UNKNOWN"
    with pytest.raises(ValidationError):
        enforce_schema(rec)

def test_encrypt_decrypt_roundtrip(tmpdb):
    _, _, key = tmpdb
    enc = Encryptor(key)
    data = b"hello world"
    ct = enc.encrypt(data)
    assert data != ct
    pt = enc.decrypt(ct)
    assert pt == data

def test_batch_upsert_and_index(tmpdb):
    db, dbdir, _ = tmpdb
    recs = [make_record("a1"), make_record("a2")]
    db.batchUpsert(recs)
    # files created
    files = os.listdir(dbdir)
    assert "a1.enc" in files and "a2.enc" in files
    # index
    res = db.query({"userID": "user1"})
    assert len(res) == 2

def test_ttl_enforced(tmpdb):
    db, dbdir, _ = tmpdb
    rec_recent = make_record("r1", days_offset=0)
    rec_old = make_record("r2", days_offset=2)
    db.batchUpsert([rec_recent, rec_old])
    # query should purge old
    res = db.query({})
    ids = [r["auditID"] for r in res]
    assert "r2" not in ids and "r1" in ids

def test_atomicity(tmpdb):
    db, dbdir, _ = tmpdb
    bad = make_record("b1")
    bad.pop("message")
    good = make_record("g1")
    with pytest.raises(Exception):
        db.batchUpsert([good, bad])
    # none persisted
    assert "g1.enc" not in os.listdir(dbdir)

def test_delete_and_softdelete(tmpdb):
    db, dbdir, _ = tmpdb
    rec = make_record("d1")
    db.batchUpsert([rec])
    # unauthorized delete
    with pytest.raises(PermissionError):
        db.delete({"auditID": "d1"}, role="auditor")
    # softdelete authorized
    db.softDelete({"auditID": "d1"}, role="auditor")
    r = db.query({"auditID": "d1"})[0]
    assert r["status"] == "archived"
    # hard delete
    db.delete({"auditID": "d1"}, role="admin")
    assert db.query({}) == []

def test_plugins(tmpdb):
    db, dbdir, _ = tmpdb
    called = {"pre": False, "post": False}
    def pre(records):
        called["pre"] = True
    def post(records):
        called["post"] = True
    db.registerPlugin("pre_upsert", pre)
    db.registerPlugin("post_upsert", post)
    rec = make_record("p1")
    db.batchUpsert([rec])
    assert called["pre"] and called["post"]
