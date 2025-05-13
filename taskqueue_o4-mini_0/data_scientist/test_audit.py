import json
import os
from ml_pipeline.audit import log_enqueue, log_dequeue

def test_audit_logs(tmp_path):
    logf = tmp_path / "audit.log"
    log_enqueue("tid1", {"p": 1}, str(logf))
    log_dequeue("tid1", str(logf))
    lines = logf.read_text().splitlines()
    assert len(lines) == 2
    e1 = json.loads(lines[0])
    e2 = json.loads(lines[1])
    assert e1["event"] == "enqueue"
    assert e2["event"] == "dequeue"
    assert e1["task_id"] == "tid1"
    assert "timestamp" in e1
