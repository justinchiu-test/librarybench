from Business_Analyst.automation.logger import AuditLogger
import time

def test_logger_records_events_with_timestamp():
    logger = AuditLogger()
    logger.log("Event A")
    time.sleep(0.01)
    logger.log("Event B")
    logs = logger.logs
    assert len(logs) == 2
    t0, e0 = logs[0]
    t1, e1 = logs[1]
    assert e0 == "Event A"
    assert e1 == "Event B"
    assert t0 < t1
