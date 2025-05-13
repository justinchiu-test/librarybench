import time
from etl.audit import AuditLogging

def test_audit_logs_order_and_content():
    a = AuditLogging()
    a.log("enqueue", "t1", tenant="teamA")
    a.log("start", "t1", tenant="teamA")
    logs = a.get_logs()
    assert len(logs) == 2
    assert logs[0]["event"] == "enqueue"
    assert logs[1]["event"] == "start"
    assert logs[0]["tenant"] == "teamA"
