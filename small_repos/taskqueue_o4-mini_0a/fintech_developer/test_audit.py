import json
from audit import AuditLogger

def test_audit_logs_chain():
    a = AuditLogger()
    a.log("t1", "action1", {"key": "value1"})
    a.log("t1", "action2", {"key": "value2"})
    logs = a.get_logs()
    assert len(logs) == 2
    # Check hash chain
    assert logs[1]["prev_hash"] == logs[0]["hash"]
    # Ensure each log has hash
    for entry in logs:
        assert "hash" in entry
