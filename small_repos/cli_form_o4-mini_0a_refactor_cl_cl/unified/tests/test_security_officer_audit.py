from security_officer.incident_form.audit import AuditLog
import time

def test_audit_log_records():
    log = AuditLog()
    log.record("start")
    time.sleep(0.001)
    log.record("stop")
    entries = log.get_log()
    assert len(entries) == 2
    assert entries[0]["action"] == "start"
    assert entries[1]["action"] == "stop"
    assert "time" in entries[0]
